"""Esquemas Pydantic de la API: validan las peticiones y definen las respuestas."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


# Usuario
class UsuarioCreate(BaseModel):
    """Datos para crear un usuario."""

    tipo: Literal["cliente", "administrador"]
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr
    direccion: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validar_direccion(self) -> "UsuarioCreate":
        """Los clientes necesitan dirección postal; los administradores no."""
        if self.tipo == "cliente" and not (self.direccion and self.direccion.strip()):
            raise ValueError("Un cliente debe tener dirección postal.")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "tipo": "cliente",
                "nombre": "Ana",
                "email": "ana@mail.com",
                "direccion": "C/ Mayor 1, Madrid",
            }
        }
    }


class UsuarioRead(BaseModel):
    """Usuario tal y como se devuelve al cliente."""

    id: str
    nombre: str
    email: str
    es_admin: bool


# Producto
class ProductoCreate(BaseModel):
    """Datos para crear un producto. Los atributos extra dependen del tipo."""

    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(min_length=1, max_length=100)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    # Solo electrónicos
    meses_garantia: Optional[int] = Field(default=None, ge=0)
    # Solo ropa
    talla: Optional[str] = Field(default=None, min_length=1)
    color: Optional[str] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validar_atributos_por_tipo(self) -> "ProductoCreate":
        """Cada tipo exige sus atributos y rechaza los que no le corresponden."""
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("Un producto electrónico requiere 'meses_garantia'.")
            if self.talla is not None or self.color is not None:
                raise ValueError("Un producto electrónico no admite 'talla' ni 'color'.")
        elif self.tipo == "ropa":
            if self.talla is None or self.color is None:
                raise ValueError("Un producto de ropa requiere 'talla' y 'color'.")
            if self.meses_garantia is not None:
                raise ValueError("Un producto de ropa no admite 'meses_garantia'.")
        else:  # genérico
            if (self.meses_garantia is not None or self.talla is not None
                    or self.color is not None):
                raise ValueError(
                    "Un producto genérico no admite 'meses_garantia', 'talla' ni 'color'."
                )
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "tipo": "electronico",
                "nombre": "Portátil",
                "precio": 899.99,
                "stock": 5,
                "meses_garantia": 24,
            }
        }
    }


class ProductoRead(BaseModel):
    """Producto tal y como se devuelve al cliente."""

    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# Pedido
class PedidoItemCreate(BaseModel):
    """Línea de un pedido en la petición: producto y cantidad."""

    producto_id: str
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    """Datos para crear un pedido."""

    cliente_id: str
    items: List[PedidoItemCreate] = Field(min_length=1)


class PedidoItemRead(BaseModel):
    """Línea de un pedido en la respuesta."""

    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    """Pedido completo en la respuesta."""

    id: str
    fecha: datetime
    cliente: UsuarioRead
    total: float
    items: List[PedidoItemRead]
