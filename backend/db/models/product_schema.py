from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey, String, Float, Boolean, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Cliente(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    celular: Mapped[str] = mapped_column(String(20))
    direccion: Mapped[str] = mapped_column(String(200))

    pedidos: Mapped[List["Pedido"]] = relationship(back_populates="cliente")


class Producto(Base):
    __tablename__ = "producto"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[Optional[str]] = mapped_column(String(200))
    precio: Mapped[float] = mapped_column(Float)
    tamaño: Mapped[Optional[str]] = mapped_column(String(50))
    image_url: Mapped[Optional[str]] = mapped_column(String(300))

    detalles_pedido: Mapped[List["DetallePedido"]] = relationship(back_populates="producto")


class Vendedor(Base):
    __tablename__ = "vendedor"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    numero: Mapped[str] = mapped_column(String(20))

    pedidos: Mapped[List["Pedido"]] = relationship(back_populates="vendedor")


class Domiciliario(Base):
    __tablename__ = "domiciliario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    numero: Mapped[str] = mapped_column(String(20))
    precio_domicilio: Mapped[float] = mapped_column(Float)

    pedidos: Mapped[List["Pedido"]] = relationship(back_populates="domiciliario")


class EstadoPedido(Base):
    __tablename__ = "estado_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    estado: Mapped[str] = mapped_column(String(50))

    pedidos: Mapped[List["Pedido"]] = relationship(back_populates="estado")


class LugarVenta(Base):
    __tablename__ = "lugar_venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    lugar_venta: Mapped[str] = mapped_column(String(100))

    pedidos: Mapped[List["Pedido"]] = relationship(back_populates="lugar_venta")


class Pedido(Base):
    __tablename__ = "pedido"

    id: Mapped[int] = mapped_column(primary_key=True)

    id_cliente: Mapped[int] = mapped_column(ForeignKey("cliente.id"))
    id_vendedor: Mapped[int] = mapped_column(ForeignKey("vendedor.id"))
    id_domiciliario: Mapped[Optional[int]] = mapped_column(ForeignKey("domiciliario.id"))
    id_estado: Mapped[int] = mapped_column(ForeignKey("estado_pedido.id"))
    id_lugar_venta: Mapped[int] = mapped_column(ForeignKey("lugar_venta.id"))

    fecha_venta: Mapped[datetime] = mapped_column(DateTime)
    fecha_entrega: Mapped[Optional[datetime]] = mapped_column(DateTime)

    referencia: Mapped[Optional[str]] = mapped_column(String(200))
    adicional: Mapped[Optional[str]] = mapped_column(String(200))

    pagado: Mapped[bool] = mapped_column(Boolean)

    cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
    vendedor: Mapped["Vendedor"] = relationship(back_populates="pedidos")
    domiciliario: Mapped[Optional["Domiciliario"]] = relationship(back_populates="pedidos")
    estado: Mapped["EstadoPedido"] = relationship(back_populates="pedidos")
    lugar_venta: Mapped["LugarVenta"] = relationship(back_populates="pedidos")

    detalles: Mapped[List["DetallePedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)

    id_pedido: Mapped[int] = mapped_column(ForeignKey("pedido.id"))
    id_producto: Mapped[int] = mapped_column(ForeignKey("producto.id"))

    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario: Mapped[float] = mapped_column(Float)

    pedido: Mapped["Pedido"] = relationship(back_populates="detalles")
    producto: Mapped["Producto"] = relationship(back_populates="detalles_pedido")