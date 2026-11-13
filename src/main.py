"""Punto de entrada y capa de exposición: API REST de la tienda online (FastAPI).

Ejecutar con:  uvicorn main:app --reload
Documentación: http://127.0.0.1:8000/docs
"""

from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, Response, status

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Cliente, Usuario
from schemas import (
    PedidoCreate,
    PedidoItemRead,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
)
from Services.Tienda_service import TiendaService

app = FastAPI(title="Tienda online")

# Única instancia del servicio (los datos se guardan en memoria).
_tienda = TiendaService()


def get_tienda() -> TiendaService:
    """Dependencia de FastAPI que proporciona el servicio a cada endpoint."""
    return _tienda


# Conversión dominio -> esquema
def usuario_a_read(usuario: Usuario) -> UsuarioRead:
    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )


def producto_a_read(producto: Producto) -> ProductoRead:
    if isinstance(producto, ProductoElectronico):
        extra = {"tipo": "electronico", "meses_garantia": producto.garantia_meses}
    elif isinstance(producto, ProductoRopa):
        extra = {"tipo": "ropa", "talla": producto.talla, "color": producto.color}
    else:
        extra = {"tipo": "generico"}
    return ProductoRead(
        id=producto.id,
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock,
        **extra,
    )


def pedido_a_read(pedido: Pedido) -> PedidoRead:
    items = [
        PedidoItemRead(
            producto_id=producto.id,
            nombre=producto.nombre,
            precio_unitario=producto.precio,
            cantidad=cantidad,
            subtotal=round(producto.precio * cantidad, 2),
        )
        for producto, cantidad in pedido.items
    ]
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente=usuario_a_read(pedido.cliente),
        total=round(pedido.calcular_total(), 2),
        items=items,
    )


# Usuarios
@app.post("/usuarios", response_model=UsuarioRead,
          status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(datos: UsuarioCreate,
                  tienda: TiendaService = Depends(get_tienda)) -> UsuarioRead:
    """Crea un nuevo usuario."""
    usuario = tienda.registrar_usuario(
        datos.tipo, datos.nombre, datos.email, datos.direccion or ""
    )
    if usuario is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de usuario no válido.")
    return usuario_a_read(usuario)


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def obtener_usuario(usuario_id: str,
                    tienda: TiendaService = Depends(get_tienda)) -> UsuarioRead:
    """Devuelve un usuario concreto."""
    usuario = tienda.buscar_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado.")
    return usuario_a_read(usuario)


@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios(tienda: TiendaService = Depends(get_tienda)) -> List[UsuarioRead]:
    """Devuelve la lista de usuarios registrados."""
    return [usuario_a_read(u) for u in tienda.usuarios]


# Productos
@app.post("/productos", response_model=ProductoRead,
          status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(datos: ProductoCreate,
                   tienda: TiendaService = Depends(get_tienda)) -> ProductoRead:
    """Crea un producto genérico, electrónico o de ropa."""
    if datos.tipo == "electronico":
        producto: Producto = ProductoElectronico(
            datos.nombre, datos.precio, datos.stock, datos.meses_garantia
        )
    elif datos.tipo == "ropa":
        producto = ProductoRopa(
            datos.nombre, datos.precio, datos.stock, datos.talla, datos.color
        )
    else:
        producto = Producto(datos.nombre, datos.precio, datos.stock)
    tienda.agregar_producto(producto)
    return producto_a_read(producto)


@app.get("/productos", response_model=List[ProductoRead], tags=["Productos"])
def listar_productos(tienda: TiendaService = Depends(get_tienda)) -> List[ProductoRead]:
    """Devuelve todos los productos del inventario."""
    return [producto_a_read(p) for p in tienda.listar_productos()]


@app.get("/productos/{producto_id}", response_model=ProductoRead, tags=["Productos"])
def obtener_producto(producto_id: str,
                     tienda: TiendaService = Depends(get_tienda)) -> ProductoRead:
    """Devuelve un producto concreto."""
    producto = tienda.buscar_producto(producto_id)
    if producto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no encontrado.")
    return producto_a_read(producto)


@app.delete("/productos/{producto_id}",
            status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def eliminar_producto(producto_id: str,
                      tienda: TiendaService = Depends(get_tienda)) -> Response:
    """Elimina un producto del inventario."""
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Pedidos
@app.post("/pedidos", response_model=PedidoRead,
          status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def crear_pedido(datos: PedidoCreate,
                 tienda: TiendaService = Depends(get_tienda)) -> PedidoRead:
    """Crea un pedido verificando cliente, producto y stock disponible."""
    usuario = tienda.buscar_usuario(datos.cliente_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    if not isinstance(usuario, Cliente):
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Solo los clientes pueden hacer pedidos.")

    # Si un producto aparece en varias líneas, se suman las cantidades.
    cantidades: Dict[str, int] = {}
    for item in datos.items:
        cantidades[item.producto_id] = cantidades.get(item.producto_id, 0) + item.cantidad

    for producto_id, cantidad in cantidades.items():
        producto = tienda.buscar_producto(producto_id)
        if producto is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                f"Producto no encontrado: {producto_id}")
        if not producto.hay_stock(cantidad):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Stock insuficiente de '{producto.nombre}' "
                f"(pedido: {cantidad}, disponible: {producto.stock}).",
            )

    pedido = tienda.realizar_pedido(datos.cliente_id, cantidades)
    if pedido is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "No se pudo crear el pedido.")
    return pedido_a_read(pedido)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=List[PedidoRead],
         tags=["Pedidos"])
def listar_pedidos_cliente(cliente_id: str,
                           tienda: TiendaService = Depends(get_tienda)) -> List[PedidoRead]:
    """Devuelve los pedidos del cliente."""
    if tienda.buscar_usuario(cliente_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    return [pedido_a_read(p) for p in tienda.listar_pedidos_usuario(cliente_id)]
