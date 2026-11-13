"""Modelo de productos de la tienda online."""

import uuid


class Producto:
    """Producto genérico de la tienda. Sirve como clase base para el resto de clases."""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto con un identificador único que se generra automáticamente."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Indica si hay stock suficiente."""
        return cantidad > 0 and self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Actualiza el stock: cantidad positiva = reposición, negativa = compra."""
        self.stock += cantidad

    def __str__(self) -> str:
        """Devuelve las características principales que teine el producto."""
        return f"[{self.id}] {self.nombre} - {self.precio:.2f} € (stock: {self.stock})"


class ProductoElectronico(Producto):
    """Producto electrónico, con meses de garantía."""

    def __init__(self, nombre: str, precio: float, stock: int,
                 garantia_meses: int) -> None:
        super().__init__(nombre, precio, stock)
        self.garantia_meses: int = garantia_meses

    def __str__(self) -> str:
        return f"{super().__str__()} | Garantía: {self.garantia_meses} meses"


class ProductoRopa(Producto):
    """Producto de ropa, con la talla y el color."""

    def __init__(self, nombre: str, precio: float, stock: int,
                 talla: str, color: str) -> None:
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
