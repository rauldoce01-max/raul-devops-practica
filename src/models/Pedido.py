"""Modelo de pedidos de la tienda online."""

import uuid
from datetime import datetime
from typing import List, Tuple

from models.Producto import Producto
from models.Usuario import Cliente


class Pedido:
    """Pedido realizado por un cliente: lista de (producto, cantidad)."""

    def __init__(self, cliente: Cliente,
                 items: List[Tuple[Producto, int]]) -> None:
        """Crea un pedido con un identificador único y con la fecha actual."""
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.items: List[Tuple[Producto, int]] = items
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Calcula el importe total según los precios y cantidades."""
        total = 0.0
        for producto, cantidad in self.items:
            total += producto.precio * cantidad
        return total

    def __str__(self) -> str:
        """Devuelve un resumen del pedido."""
        texto = f"Pedido {self.id} ({self.fecha.strftime('%d/%m/%Y %H:%M:%S')})\n"
        texto += f"Cliente: {self.cliente.nombre}\n"
        for producto, cantidad in self.items:
            texto += f"  - {cantidad} x {producto.nombre} ({producto.precio:.2f} €)\n"
        texto += f"Total: {self.calcular_total():.2f} €"
        return texto
