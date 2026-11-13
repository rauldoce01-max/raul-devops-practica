"""Servicio que centraliza las operaciones de la tienda online."""

from typing import Dict, List, Optional, Tuple

from models.Pedido import Pedido
from models.Producto import Producto
from models.Usuario import Administrador, Cliente, Usuario


class TiendaService:
    """Intermediario entre los usuarios y los productos de la tienda."""

    def __init__(self) -> None:
        self.usuarios: List[Usuario] = []
        self.productos: List[Producto] = []
        self.pedidos: List[Pedido] = []

    def buscar_usuario(self, usuario_id: str) -> Optional[Usuario]:
        """Devuelve el usuario con ese id, o None si ese usuario no existe."""
        for usuario in self.usuarios:
            if usuario.id == usuario_id:
                return usuario
        return None

    def buscar_producto(self, producto_id: str) -> Optional[Producto]:
        """Devuelve el producto con ese id, o None si no existe."""
        for producto in self.productos:
            if producto.id == producto_id:
                return producto
        return None

    def registrar_usuario(self, tipo: str, nombre: str, email: str,
                          direccion: str = "") -> Optional[Usuario]:
        """Registra un usuario de tipo cliente o administrador."""
        if tipo == "cliente":
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            print("Tipo de usuario no válido (debe ser 'cliente' o 'administrador').")
            return None
        self.usuarios.append(usuario)
        return usuario

    def agregar_producto(self, producto: Producto) -> None:
        """Añade un producto al inventario."""
        self.productos.append(producto)

    def eliminar_producto(self, producto_id: str) -> bool:
        """Elimina un producto por su id. Devuelve False si no existe."""
        producto = self.buscar_producto(producto_id)
        if producto is None:
            print("No se puede eliminar,el producto no existe.")
            return False
        self.productos.remove(producto)
        return True

    def listar_productos(self) -> List[Producto]:
        """Devuelve todos los productos del inventario."""
        return self.productos

    def realizar_pedido(self, usuario_id: str,
                        items: Dict[str, int]) -> Optional[Pedido]:
        """Crea un pedido a partir de un diccionario {id_producto: cantidad}.

        Comprueba que el usuario existe y que hay stock de todos los productos
        antes de quitar nada del inventario. Si hay algun fallo, devuelve None.
        """
        usuario = self.buscar_usuario(usuario_id)
        if usuario is None:
            print("Pedido rechazado: el usuario no existe.")
            return None
        if not isinstance(usuario, Cliente):
            print("Pedido rechazado: solo los clientes pueden hacer pedidos.")
            return None
        if len(items) == 0:
            print("Pedido rechazado: no hay productos en el pedido.")
            return None

        # Primero comprobamos todo, sin modificar el inventario
        lineas: List[Tuple[Producto, int]] = []
        for producto_id in items:
            cantidad = items[producto_id]
            producto = self.buscar_producto(producto_id)
            if producto is None:
                print("Pedido rechazado: uno de los productos no existe.")
                return None
            if not producto.hay_stock(cantidad):
                print(f"Pedido rechazado: stock insuficiente de {producto.nombre} "
                      f"(pedido: {cantidad}, disponible: {producto.stock}).")
                return None
            lineas.append((producto, cantidad))

        # Creamos el pedido y descontamos el stock
        pedido = Pedido(usuario, lineas)
        for producto, cantidad in lineas:
            producto.actualizar_stock(-cantidad)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> List[Pedido]:
        """Devuelve los pedidos de un usuario ordenados por fecha."""
        pedidos_usuario: List[Pedido] = []
        for pedido in self.pedidos:
            if pedido.cliente.id == usuario_id:
                pedidos_usuario.append(pedido)
        return sorted(pedidos_usuario, key=lambda pedido: pedido.fecha)
