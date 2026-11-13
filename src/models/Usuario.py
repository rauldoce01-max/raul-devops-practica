"""Modelo de usuarios de la tienda online."""

import uuid


class Usuario:
    """Persona que interactúa con la tienda."""

    def __init__(self, nombre: str, email: str) -> None:
        """Crea un usuario con un identificador único generado automáticamente."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Por defecto, un usuario no es administrador."""
        return False

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} <{self.email}>"


class Cliente(Usuario):
    """Usuario que compra en la tienda, con dirección postal."""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        return f"{super().__str__()} | Cliente | Dirección: {self.direccion}"


class Administrador(Usuario):
    """Usuario que gestiona la tienda de la tienda."""

    def is_admin(self) -> bool:
        """Un administrador siempre devuelve True."""
        return True

    def __str__(self) -> str:
        return f"{super().__str__()} | Administrador"
