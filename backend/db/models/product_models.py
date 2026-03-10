from pydantic import BaseModel
from typing import Optional


class Cliente(BaseModel):
    id: int
    nombre: str
    celular: str
    direccion: str


class Product(BaseModel):
    id: int
    precio: float
    description: str
    tamaño: str
    image_url: str


class Domiciliario(BaseModel):
    id: int
    precio_domicilio: str
    nombre: str
    numero: str


class Vendedor(BaseModel):
    id: int
    nombre: str
    numero: str


class EstadoPedido(BaseModel):
    id: int
    estado: str


class LugarVenta(BaseModel):
    id: int
    lugar_venta: str


class Pedido(BaseModel):
    id: int
    fecha_venta : str
    fecha_entrega: str
    referencia: str
    adicional: str
    pagado: bool
    cantidad: int