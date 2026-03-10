import csv
import os
import re
import sys
from datetime import datetime
from dotenv import load_dotenv

# Asegurar que el path incluya la raíz para importar el backend
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Cargar variables de entorno
load_dotenv()

from backend.db.settings.postgress_settings import PostgresSettings
from backend.db.provider.postgress_provider import PostgresProvider
from backend.db.repository.postgress_repository import PostgressRepository
from backend.db.models.product_schema import (
    Base, Cliente, Producto, Vendedor, Domiciliario, 
    EstadoPedido, LugarVenta, Pedido, DetallePedido
)

def clean_currency(value):
    if not value or not isinstance(value, str):
        return 0.0
    # Quitar $, puntos de miles, comas y espacios
    clean_val = re.sub(r'[^\d]', '', value)
    try:
        return float(clean_val)
    except ValueError:
        return 0.0

def parse_date(date_str):
    if not date_str or not isinstance(date_str, str) or date_str.strip() == "":
        return None
    # Intentar varios formatos comunes
    formats = ["%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def find_column(headers, possible_names):
    """Encuentra un nombre de columna que coincida con alguno de los nombres posibles."""
    for header in headers:
        normalized_header = header.strip().lower()
        normalized_header = re.sub(r'[^\w\s]', '', normalized_header)
        for name in possible_names:
            if name.lower() in normalized_header:
                return header
    return None

def get_or_create(session, model, **kwargs):
    """Auxiliar para buscar o crear registros usando la sesión compartida."""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance

def run_etl(csv_path):
    print(f"--- Iniciando ETL de {csv_path} usando el sistema del proyecto ---")
    # 1. Configuración usando el sistema del proyecto
    settings = PostgresSettings()
    provider = PostgresProvider(settings)
    # 2. Asegurar tablas (usando el engine del provider)
    try:
        print("Verificando esquema...")
        Base.metadata.create_all(provider._engine)
    except Exception as e:
        print(f"Error al crear tablas: {e}")
        return

    # Intentar detectar la codificación
    encodings = ['utf-8-sig', 'latin-1', 'cp1252', 'utf-8']
    f = None
    for enc in encodings:
        try:
            f = open(csv_path, mode='r', encoding=enc)
            f.readline()
            f.seek(0)
            print(f"Codificación detectada: {enc}")
            break
        except Exception:
            if f: f.close()
            continue
    if not f:
        print("No se pudo abrir el archivo CSV.")
        return

    # 3. Proceso de ETL dentro de un contexto de sesión del provider
    try:
        f.readline() # Saltar ARBOL...
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        # Mapeo de columnas
        col_fecha = find_column(headers, ['fecha de venta', 'fecha'])
        col_entrega = find_column(headers, ['entrega', 'dia de entrega'])
        col_cliente = find_column(headers, ['cliente'])
        col_celular = find_column(headers, ['celular'])
        col_direccion = find_column(headers, ['direcci', 'direccion'])
        col_diseno = find_column(headers, ['dise', 'disenio']) # Este será la REFERENCIA
        col_vendedor = find_column(headers, ['vendedor'])
        col_repartidor = find_column(headers, ['repartidor', 'domiciliario'])
        col_estado = find_column(headers, ['estado del pedido', 'estado'])
        col_lugar = find_column(headers, ['lugar de venta', 'lugar'])
        col_precio = find_column(headers, ['precio'])
        col_domicilio = find_column(headers, ['domicilio'])
        col_adicional = find_column(headers, ['adicional'])
        col_pagar = find_column(headers, ['por pagar', 'pagado'])

        count = 0
        with provider.get_session_context() as session:
            for row in reader:
                if not col_fecha or not row.get(col_fecha):
                    continue
                
                # A. Cliente
                cliente_nombre = (row.get(col_cliente) or "cliente anonimo").strip().lower()
                cliente = get_or_create(
                    session, Cliente, 
                    nombre=cliente_nombre[:100],
                    celular=(row.get(col_celular) or "")[:20],
                    direccion=(row.get(col_direccion) or "")[:200]
                )
                
                # B. Vendedor
                vendedor_nombre = (row.get(col_vendedor) or "desconocido").strip().lower()
                vendedor = get_or_create(
                    session, Vendedor,
                    nombre=vendedor_nombre[:100],
                    numero=""
                )
                
                # C. Domiciliario
                repartidor_nombre = (row.get(col_repartidor) or "").strip().lower()
                precio_domicilio = clean_currency(row.get(col_domicilio))
                domiciliario = None
                if repartidor_nombre:
                    domiciliario = get_or_create(
                        session, Domiciliario,
                        nombre=repartidor_nombre[:100],
                        numero="",
                        precio_domicilio=precio_domicilio
                    )
                
                # D. Estado
                estado_str = (row.get(col_estado) or "pendiente").strip().lower()
                estado = get_or_create(
                    session, EstadoPedido,
                    estado=estado_str[:50]
                )
                
                # E. Lugar de Venta
                lugar_str = (row.get(col_lugar) or "desconocido").strip().lower()
                lugar = get_or_create(
                    session, LugarVenta,
                    lugar_venta=lugar_str[:100]
                )
                
                # F. Producto
                # Si el diseño es la referencia, usamos una categoría general o el mismo nombre para el producto
                # Aquí podrías ajustar si prefieres que el producto tenga un nombre genérico
                diseno_val = (row.get(col_diseno) or "sin diseño").strip()
                producto_nombre = diseno_val.lower()[:100]
                precio_unitario = clean_currency(row.get(col_precio))
                
                producto = get_or_create(
                    session, Producto,
                    nombre=producto_nombre,
                    precio=precio_unitario
                )
                
                # G. Pedido (¡Aquí la REFERENCIA es el DISEÑO!)
                fecha_venta = parse_date(row.get(col_fecha))
                fecha_entrega = parse_date(row.get(col_entrega))
                por_pagar_str = str(row.get(col_pagar) or "").strip().upper()
                pagado = (por_pagar_str == 'FALSE' or por_pagar_str == '0' or por_pagar_str == '')
                
                pedido = Pedido(
                    id_cliente=cliente.id,
                    id_vendedor=vendedor.id,
                    id_domiciliario=domiciliario.id if domiciliario else None,
                    id_estado=estado.id,
                    id_lugar_venta=lugar.id,
                    fecha_venta=fecha_venta or datetime.now(),
                    fecha_entrega=fecha_entrega,
                    adicional=(row.get(col_adicional) or "")[:200],
                    referencia=diseno_val[:200], # <--- DISEÑO mapeado a REFERENCIA
                    pagado=pagado
                )
                session.add(pedido)
                session.flush() # Importante para obtener el pedido.id
                
                # H. Detalle del Pedido
                detalle = DetallePedido(
                    id_pedido=pedido.id,
                    id_producto=producto.id,
                    cantidad=1,
                    precio_unitario=precio_unitario
                )
                session.add(detalle)
                
                count += 1
                if count % 50 == 0:
                    print(f"Insertados {count} registros...")
            
            # El commit ocurre automáticamente al salir del contexto get_session_context si no hay errores
            print(f"Commit exitoso: {count} registros procesados.")

    except Exception as e:
        print(f"Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if f: f.close()
        provider.close()

if __name__ == "__main__":
    CSV_FILE = "Iluminaria Store - PEDIDOS.csv"
    if os.path.exists(CSV_FILE):
        run_etl(CSV_FILE)
    else:
        print(f"CSV no encontrado: {CSV_FILE}")
