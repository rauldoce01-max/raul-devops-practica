# Tienda online - Práctica DevOps

**Autor:** Raúl

API REST de una tienda online desarrollada con **FastAPI** y **Pydantic**. Permite registrar usuarios (clientes y administradores), gestionar productos (genéricos, electrónicos y de ropa) y crear pedidos comprobando el stock disponible. Los datos se guardan en memoria.

## Estructura

```
.
├── dockerfile
├── .dockerignore
├── requirements.txt
├── README.md
└── src/
    ├── main.py              # API FastAPI (endpoints)
    ├── schemas.py           # Esquemas Pydantic
    ├── models/              # Producto, Usuario, Pedido
    └── Services/            # TiendaService
```

## Ejecución local (sin Docker)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --app-dir src --reload
```

Documentación: http://127.0.0.1:8000/docs

## Docker

### Construir la imagen
```bash
docker build -t rauldoce12/tienda-api:1.0 .
```

### Descargar la imagen publicada
```bash
docker pull rauldoce12/tienda-api:1.0
```

### Ejecutar
```bash
docker run -d -p 8000:8000 --name tienda rauldoce12/tienda-api:1.0
```
Con otro puerto en el host:
```bash
docker run -d -p 9000:8000 --name tienda rauldoce12/tienda-api:1.0
```

### Variables de entorno
La aplicación no necesita variables de entorno. La imagen define internamente `PYTHONUNBUFFERED=1` y `PYTHONDONTWRITEBYTECODE=1`.

### Salida esperada y pruebas
`docker logs tienda` debe mostrar:
```
Uvicorn running on http://0.0.0.0:8000
```

Documentación interactiva: http://localhost:8000/docs

Endpoints para probar (en este orden):

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/usuarios` | Crear cliente o administrador |
| GET | `/usuarios` | Listar usuarios |
| GET | `/usuarios/{usuario_id}` | Obtener un usuario |
| POST | `/productos` | Crear producto (generico, electronico, ropa) |
| GET | `/productos` | Listar productos |
| GET | `/productos/{producto_id}` | Obtener un producto |
| DELETE | `/productos/{producto_id}` | Eliminar un producto |
| POST | `/pedidos` | Crear pedido (descuenta stock) |
| GET | `/usuarios/{cliente_id}/pedidos` | Pedidos de un cliente |

Ejemplo con curl:
```bash
curl -X POST http://localhost:8000/usuarios -H "Content-Type: application/json" \
  -d '{"tipo":"cliente","nombre":"Ana","email":"ana@mail.com","direccion":"C/ Mayor 1, Madrid"}'

curl -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
  -d '{"tipo":"electronico","nombre":"Portátil","precio":899.99,"stock":5,"meses_garantia":24}'

curl -X POST http://localhost:8000/pedidos -H "Content-Type: application/json" \
  -d '{"cliente_id":"<ID_CLIENTE>","items":[{"producto_id":"<ID_PRODUCTO>","cantidad":2}]}'
```
Respuestas esperadas: `201 Created` al crear; `404` si el usuario o el producto no existen; `403` si un administrador intenta hacer un pedido; `409` si no hay stock suficiente; `422` si los datos no son válidos.

### Parar y eliminar el contenedor
```bash
docker stop tienda && docker rm tienda
```
