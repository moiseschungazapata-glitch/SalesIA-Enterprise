# Fase 02 - Contratos iniciales de la API

## 1. Control del documento

| Campo | Valor |
| --- | --- |
| Proyecto | SalesIA Enterprise |
| Fase | 02 - Arquitectura tecnica |
| Documento | Contratos iniciales de la API |
| Version de API | v1 |
| Prefijo | `/api/v1` |
| Formato | JSON |
| Estado | Definido para la primera version |

## 2. Proposito

Este documento establece el acuerdo entre el frontend React y el backend
FastAPI. Define las operaciones disponibles, los permisos, los datos de entrada,
las respuestas y los errores esperados.

En esta fase los contratos son diseño. Los schemas Pydantic, servicios y
endpoints se implementaran en la fase 05. FastAPI generara OpenAPI y Swagger UI
a partir de esa implementacion.

## 3. Convenciones generales

### 3.1 Direcciones

- Todos los endpoints de negocio comienzan con `/api/v1`.
- Los recursos usan nombres en plural y en ingles.
- Los identificadores se incluyen como `{id}` en la direccion.
- No se publican endpoints `DELETE` en la primera version.
- Los registros con historial se desactivan mediante `PATCH`.

### 3.2 Formato de datos

- Las propiedades JSON usan `snake_case`.
- Los identificadores son enteros positivos.
- Las fechas de consulta usan `YYYY-MM-DD`.
- Las fechas y horas usan ISO 8601 con zona horaria.
- Los importes monetarios se representan como texto decimal, por ejemplo
  `"125.50"`.
- La moneda de la primera version es `PEN`.
- Los valores booleanos usan `true` y `false`.
- Los campos opcionales pueden ser `null` cuando el contrato lo indique.

### 3.3 Autenticacion

Los endpoints protegidos reciben el token en el encabezado:

```http
Authorization: Bearer <access_token>
```

La estrategia detallada del token, su duracion y la proteccion de contrasenas se
encuentran en
[Autenticacion y permisos](../architecture/fase-02-autenticacion-permisos.md).

### 3.4 Respuesta paginada

Todas las listas paginadas usan esta estructura:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

Reglas:

- `page` comienza en 1.
- `page_size` usa 20 por defecto.
- `page_size` acepta valores entre 1 y 100.
- Las listas se ordenan de manera estable para evitar registros repetidos entre
  paginas.

### 3.5 Respuesta de error

Todos los errores controlados usan esta estructura:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "El producto no tiene stock suficiente",
    "details": {
      "product_id": 8,
      "available": 1,
      "requested": 2
    }
  }
}
```

`details` puede ser un objeto vacio cuando no existe informacion adicional
segura para entregar al cliente.

### 3.6 Codigos HTTP

| Codigo | Uso |
| --- | --- |
| `200 OK` | Consulta o actualizacion correcta. |
| `201 Created` | Registro creado correctamente. |
| `400 Bad Request` | La solicitud contradice una regla general. |
| `401 Unauthorized` | Faltan credenciales o el token no es valido. |
| `403 Forbidden` | El usuario no tiene permiso. |
| `404 Not Found` | El recurso solicitado no existe. |
| `409 Conflict` | Existe un duplicado o conflicto con el estado actual. |
| `422 Unprocessable Entity` | Los campos no cumplen el formato requerido. |
| `500 Internal Server Error` | Error inesperado, sin detalles internos. |

## 4. Resumen de endpoints

| Metodo | Endpoint | Permiso principal | Resultado |
| --- | --- | --- | --- |
| POST | `/auth/login` | Publico | Iniciar sesion. |
| GET | `/auth/me` | Usuario autenticado | Consultar sesion actual. |
| GET | `/users` | Administrador | Listar usuarios. |
| POST | `/users` | Administrador | Crear usuario. |
| GET | `/users/{id}` | Administrador | Consultar usuario. |
| PATCH | `/users/{id}` | Administrador | Actualizar o desactivar usuario. |
| GET | `/customers` | Todos los roles | Listar clientes. |
| POST | `/customers` | Administrador | Crear cliente. |
| GET | `/customers/{id}` | Todos los roles | Consultar cliente. |
| PATCH | `/customers/{id}` | Administrador | Actualizar o desactivar cliente. |
| GET | `/categories` | Todos los roles | Listar categorias. |
| POST | `/categories` | Administrador | Crear categoria. |
| PATCH | `/categories/{id}` | Administrador | Actualizar o desactivar categoria. |
| GET | `/products` | Todos los roles | Listar productos. |
| POST | `/products` | Administrador | Crear producto. |
| GET | `/products/{id}` | Todos los roles | Consultar producto. |
| PATCH | `/products/{id}` | Administrador | Actualizar o desactivar producto. |
| GET | `/inventory` | Todos los roles | Consultar existencias. |
| GET | `/inventory/movements` | Administrador y gerente | Consultar movimientos. |
| POST | `/inventory/movements` | Administrador | Registrar movimiento manual. |
| GET | `/sales` | Segun rol | Listar ventas autorizadas. |
| POST | `/sales` | Administrador y vendedor | Registrar venta. |
| GET | `/sales/{id}` | Segun rol | Consultar detalle autorizado. |
| GET | `/dashboard/summary` | Administrador y gerente | Consultar resumen comercial. |

Los endpoints de esta tabla se muestran sin `/api/v1` para facilitar la lectura.
La direccion publicada siempre incluye el prefijo completo.

## 5. Autenticacion

### 5.1 Iniciar sesion

```http
POST /api/v1/auth/login
```

**Permiso:** publico.

**Entrada:**

```json
{
  "email": "vendedor@empresa.pe",
  "password": "contrasena-del-usuario"
}
```

**Respuesta `200 OK`:**

```json
{
  "access_token": "token-generado",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 4,
    "name": "Luis Perez",
    "email": "vendedor@empresa.pe",
    "role": "seller"
  }
}
```

**Errores esperados:**

- `401 INVALID_CREDENTIALS`: correo o contraseña incorrectos.
- `403 USER_INACTIVE`: usuario desactivado.
- `422 VALIDATION_ERROR`: correo o contraseña sin formato valido.

### 5.2 Consultar usuario autenticado

```http
GET /api/v1/auth/me
```

**Permiso:** cualquier usuario autenticado.

**Respuesta `200 OK`:**

```json
{
  "id": 4,
  "name": "Luis Perez",
  "email": "vendedor@empresa.pe",
  "role": "seller",
  "active": true
}
```

**Errores esperados:** `401 INVALID_TOKEN` y `403 USER_INACTIVE`.

## 6. Usuarios

### 6.1 Campos del recurso

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | entero | Generado por el sistema. |
| `name` | texto | Obligatorio. |
| `email` | texto | Obligatorio y unico. |
| `role` | texto | `administrator`, `seller` o `manager`. |
| `active` | booleano | `true` al crear. |
| `created_at` | fecha-hora | Generada por el sistema. |
| `updated_at` | fecha-hora | Generada por el sistema. |

La contraseña solo se recibe al crear o cambiar credenciales. Nunca aparece en
una respuesta.

### 6.2 Listar usuarios

```http
GET /api/v1/users?page=1&page_size=20&search=luis&active=true&role=seller
```

**Permiso:** administrador.

**Respuesta:** lista paginada de usuarios.

### 6.3 Crear usuario

```http
POST /api/v1/users
```

**Permiso:** administrador.

**Entrada:**

```json
{
  "name": "Luis Perez",
  "email": "vendedor@empresa.pe",
  "password": "contrasena-inicial",
  "role": "seller"
}
```

**Respuesta:** `201 Created` con el usuario creado, sin contraseña.

**Errores esperados:**

- `409 EMAIL_ALREADY_EXISTS`.
- `422 VALIDATION_ERROR`.

### 6.4 Consultar usuario

```http
GET /api/v1/users/{id}
```

**Permiso:** administrador.

**Respuesta:** `200 OK` con el recurso usuario.

**Error esperado:** `404 USER_NOT_FOUND`.

### 6.5 Actualizar usuario

```http
PATCH /api/v1/users/{id}
```

**Permiso:** administrador.

**Entrada:** puede incluir `name`, `email`, `role`, `active` o `new_password`.
Los campos omitidos mantienen su valor.

**Respuesta:** `200 OK` con el usuario actualizado, sin contraseña.

**Errores esperados:** `404 USER_NOT_FOUND`, `409 EMAIL_ALREADY_EXISTS` y
`422 VALIDATION_ERROR`.

## 7. Clientes

### 7.1 Campos del recurso

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | entero | Generado por el sistema. |
| `customer_type` | texto | `person` o `company`. |
| `document_type` | texto | `DNI` o `RUC`. |
| `document_number` | texto | Unico; DNI de 8 digitos o RUC de 11 digitos. |
| `name` | texto | Nombre completo o razon social. |
| `phone` | texto o null | Opcional. |
| `email` | texto o null | Opcional; debe tener formato valido. |
| `address` | texto o null | Opcional. |
| `active` | booleano | Indica si puede usarse en nuevas ventas. |
| `created_at` | fecha-hora | Generada por el sistema. |
| `updated_at` | fecha-hora | Generada por el sistema. |

`person` utiliza DNI y `company` utiliza RUC en la primera version.

### 7.2 Listar clientes

```http
GET /api/v1/customers?page=1&page_size=20&search=ana&active=true
```

**Permiso:** administrador, vendedor o gerente.

**Respuesta:** lista paginada de clientes.

### 7.3 Crear cliente

```http
POST /api/v1/customers
```

**Permiso:** administrador.

**Entrada:**

```json
{
  "customer_type": "person",
  "document_type": "DNI",
  "document_number": "12345678",
  "name": "Ana Torres",
  "phone": "999888777",
  "email": "ana@example.com",
  "address": "Lima"
}
```

**Respuesta:** `201 Created` con el cliente creado y `active: true`.

**Errores esperados:**

- `409 DOCUMENT_ALREADY_EXISTS`.
- `422 INVALID_DOCUMENT`.
- `422 VALIDATION_ERROR`.

### 7.4 Consultar cliente

```http
GET /api/v1/customers/{id}
```

**Permiso:** administrador, vendedor o gerente.

**Respuesta:** `200 OK` con el recurso cliente.

**Error esperado:** `404 CUSTOMER_NOT_FOUND`.

### 7.5 Actualizar cliente

```http
PATCH /api/v1/customers/{id}
```

**Permiso:** administrador.

**Entrada:** puede incluir `name`, `phone`, `email`, `address` o `active`.
El tipo y numero de documento no se modifican en la primera version.

**Respuesta:** `200 OK` con el cliente actualizado.

**Errores esperados:** `404 CUSTOMER_NOT_FOUND` y `422 VALIDATION_ERROR`.

## 8. Categorias

### 8.1 Campos del recurso

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | entero | Generado por el sistema. |
| `name` | texto | Obligatorio y unico. |
| `description` | texto o null | Opcional. |
| `active` | booleano | Indica si admite productos activos nuevos. |

### 8.2 Listar categorias

```http
GET /api/v1/categories?page=1&page_size=20&search=tecnologia&active=true
```

**Permiso:** administrador, vendedor o gerente.

**Respuesta:** lista paginada de categorias.

### 8.3 Crear categoria

```http
POST /api/v1/categories
```

**Permiso:** administrador.

**Entrada:**

```json
{
  "name": "Tecnologia",
  "description": "Productos tecnologicos"
}
```

**Respuesta:** `201 Created` con la categoria creada.

**Error esperado:** `409 CATEGORY_ALREADY_EXISTS`.

### 8.4 Actualizar categoria

```http
PATCH /api/v1/categories/{id}
```

**Permiso:** administrador.

**Entrada:** puede incluir `name`, `description` o `active`.

**Respuesta:** `200 OK` con la categoria actualizada.

**Errores esperados:** `404 CATEGORY_NOT_FOUND` y
`409 CATEGORY_ALREADY_EXISTS`.

## 9. Productos

### 9.1 Campos del recurso

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | entero | Generado por el sistema. |
| `sku` | texto | Codigo unico. |
| `name` | texto | Obligatorio. |
| `description` | texto o null | Opcional. |
| `category_id` | entero | Categoria existente y activa. |
| `unit_price` | decimal como texto | Mayor que cero. |
| `stock` | entero | Calculado por movimientos; nunca negativo. |
| `active` | booleano | Indica si puede venderse. |
| `created_at` | fecha-hora | Generada por el sistema. |
| `updated_at` | fecha-hora | Generada por el sistema. |

### 9.2 Listar productos

```http
GET /api/v1/products?page=1&page_size=20&search=teclado&category_id=2&active=true
```

**Permiso:** administrador, vendedor o gerente.

**Respuesta:** lista paginada de productos con stock actual.

### 9.3 Crear producto

```http
POST /api/v1/products
```

**Permiso:** administrador.

**Entrada:**

```json
{
  "sku": "TEC-001",
  "name": "Teclado mecanico",
  "description": null,
  "category_id": 2,
  "unit_price": "150.00",
  "initial_stock": 10
}
```

Si `initial_stock` es mayor que cero, el backend creara un movimiento de stock
inicial junto con el producto. El valor por defecto es cero.

**Respuesta:** `201 Created` con el producto creado y su stock actual.

**Errores esperados:**

- `404 CATEGORY_NOT_FOUND`.
- `409 SKU_ALREADY_EXISTS`.
- `409 CATEGORY_INACTIVE`.
- `422 INVALID_PRICE`.
- `422 INVALID_QUANTITY`.

### 9.4 Consultar producto

```http
GET /api/v1/products/{id}
```

**Permiso:** administrador, vendedor o gerente.

**Respuesta:** `200 OK` con el producto y su stock actual.

**Error esperado:** `404 PRODUCT_NOT_FOUND`.

### 9.5 Actualizar producto

```http
PATCH /api/v1/products/{id}
```

**Permiso:** administrador.

**Entrada:** puede incluir `sku`, `name`, `description`, `category_id`,
`unit_price` o `active`. No acepta `stock`; el stock cambia mediante movimientos.

**Respuesta:** `200 OK` con el producto actualizado.

**Errores esperados:** `404 PRODUCT_NOT_FOUND`, `409 SKU_ALREADY_EXISTS`,
`409 CATEGORY_INACTIVE` y `422 VALIDATION_ERROR`.

## 10. Inventario

### 10.1 Consultar existencias

```http
GET /api/v1/inventory?page=1&page_size=20&search=teclado&active=true
```

**Permiso:** administrador, vendedor o gerente.

**Respuesta:**

```json
{
  "items": [
    {
      "product_id": 8,
      "sku": "TEC-001",
      "product_name": "Teclado mecanico",
      "stock": 10,
      "active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### 10.2 Consultar movimientos

```http
GET /api/v1/inventory/movements?page=1&page_size=20&product_id=8&type=entry&date_from=2026-10-01&date_to=2026-10-31
```

**Permiso:** administrador o gerente.

**Respuesta:** lista paginada con identificador, producto, tipo, cantidad, stock
resultante, motivo, usuario, venta relacionada y fecha.

### 10.3 Registrar movimiento manual

```http
POST /api/v1/inventory/movements
```

**Permiso:** administrador.

**Entrada:**

```json
{
  "product_id": 8,
  "movement_type": "entry",
  "quantity": 5,
  "reason": "Reposicion de mercaderia"
}
```

Tipos manuales permitidos:

- `initial`: stock inicial, solamente cuando el producto aun no tiene movimientos.
- `entry`: entrada de mercaderia.
- `adjustment_in`: correccion que aumenta el stock.
- `adjustment_out`: correccion que reduce el stock.

La cantidad siempre es positiva. El tipo determina si aumenta o reduce el stock.
Las salidas por venta usan `sale` y solo las genera el sistema.

**Respuesta:** `201 Created` con el movimiento y el stock resultante.

**Errores esperados:**

- `404 PRODUCT_NOT_FOUND`.
- `409 PRODUCT_INACTIVE`.
- `409 INITIAL_STOCK_ALREADY_RECORDED`.
- `409 INSUFFICIENT_STOCK`.
- `422 INVALID_QUANTITY`.

## 11. Ventas

### 11.1 Listar ventas

```http
GET /api/v1/sales?page=1&page_size=20&number=V-000120&date_from=2026-10-01&date_to=2026-10-31&customer_id=15&seller_id=4&status=confirmed
```

**Permisos:**

- Administrador y gerente: todas las ventas que cumplan los filtros.
- Vendedor: solamente las ventas registradas por el propio usuario; no puede
  consultar ventas ajenas cambiando `seller_id`.

**Respuesta:** lista paginada con numero, fecha, cliente, vendedor, estado,
moneda, total y metodo de pago.

### 11.2 Registrar venta

```http
POST /api/v1/sales
Authorization: Bearer <access_token>
Idempotency-Key: <uuid-generado-por-el-cliente>
Content-Type: application/json
```

**Permiso:** administrador o vendedor.

`Idempotency-Key` es obligatorio. Si el frontend repite accidentalmente una
solicitud con la misma clave, el backend devuelve la venta ya creada en lugar de
registrar otra.

**Entrada:**

```json
{
  "customer_id": 15,
  "payment_method": "cash",
  "items": [
    {
      "product_id": 8,
      "quantity": 2
    },
    {
      "product_id": 11,
      "quantity": 1
    }
  ]
}
```

Metodos de pago iniciales:

- `cash`: efectivo.
- `card`: tarjeta.
- `bank_transfer`: transferencia bancaria.

El frontend no envia precios, subtotales, importe pagado ni total. El backend
obtiene los precios vigentes, calcula los importes y registra un pago por el
total para impedir manipulaciones.

**Respuesta `201 Created`:**

```json
{
  "id": 120,
  "number": "V-000120",
  "status": "confirmed",
  "created_at": "2026-10-01T10:30:00-05:00",
  "customer": {
    "id": 15,
    "name": "Ana Torres"
  },
  "seller": {
    "id": 4,
    "name": "Luis Perez"
  },
  "items": [
    {
      "product_id": 8,
      "sku": "TEC-001",
      "product_name": "Teclado mecanico",
      "quantity": 2,
      "unit_price": "150.00",
      "subtotal": "300.00"
    },
    {
      "product_id": 11,
      "sku": "TEC-002",
      "product_name": "Mouse",
      "quantity": 1,
      "unit_price": "50.00",
      "subtotal": "50.00"
    }
  ],
  "payment": {
    "method": "cash",
    "amount": "350.00"
  },
  "currency": "PEN",
  "total": "350.00"
}
```

La venta, sus detalles, el pago y las salidas de inventario se confirman dentro
de una sola transaccion.

**Errores esperados:**

- `404 CUSTOMER_NOT_FOUND`.
- `404 PRODUCT_NOT_FOUND`.
- `409 CUSTOMER_INACTIVE`.
- `409 PRODUCT_INACTIVE`.
- `409 INSUFFICIENT_STOCK`.
- `409 IDEMPOTENCY_KEY_REUSED`: la clave ya se uso con datos diferentes.
- `422 EMPTY_SALE`.
- `422 INVALID_QUANTITY`.
- `422 INVALID_PAYMENT_METHOD`.

### 11.3 Consultar venta

```http
GET /api/v1/sales/{id}
```

**Permisos:**

- Administrador y gerente: cualquier venta.
- Vendedor: solamente una venta registrada por el propio usuario.

**Respuesta:** `200 OK` con la misma estructura detallada de la creacion.

**Errores esperados:** `404 SALE_NOT_FOUND` y `403 SALE_ACCESS_DENIED`.

No se definen `PATCH` ni `DELETE` para ventas confirmadas.

## 12. Dashboard

### 12.1 Consultar resumen comercial

```http
GET /api/v1/dashboard/summary?date_from=2026-10-01&date_to=2026-10-31
```

**Permiso:** administrador o gerente.

Si no se indica el periodo, se utiliza el mes actual en `America/Lima`.

**Respuesta `200 OK`:**

```json
{
  "period": {
    "date_from": "2026-10-01",
    "date_to": "2026-10-31",
    "timezone": "America/Lima"
  },
  "currency": "PEN",
  "total_sales": 25,
  "total_revenue": "8500.00",
  "average_ticket": "340.00",
  "top_products": [
    {
      "product_id": 8,
      "product_name": "Teclado mecanico",
      "quantity_sold": 12,
      "revenue": "1800.00"
    }
  ],
  "recent_sales": []
}
```

Solamente se consideran ventas confirmadas.

**Errores esperados:** `422 INVALID_DATE_RANGE` y `403 FORBIDDEN`.

## 13. Catalogo inicial de errores

| Codigo de aplicacion | HTTP | Significado |
| --- | --- | --- |
| `VALIDATION_ERROR` | 422 | Uno o mas campos son invalidos. |
| `INVALID_CREDENTIALS` | 401 | Credenciales incorrectas. |
| `INVALID_TOKEN` | 401 | Token ausente, vencido o invalido. |
| `FORBIDDEN` | 403 | Rol sin permiso para la operacion. |
| `USER_INACTIVE` | 403 | Usuario desactivado. |
| `USER_NOT_FOUND` | 404 | Usuario inexistente. |
| `CUSTOMER_NOT_FOUND` | 404 | Cliente inexistente. |
| `PRODUCT_NOT_FOUND` | 404 | Producto inexistente. |
| `CATEGORY_NOT_FOUND` | 404 | Categoria inexistente. |
| `SALE_NOT_FOUND` | 404 | Venta inexistente o no visible. |
| `EMAIL_ALREADY_EXISTS` | 409 | Correo registrado anteriormente. |
| `DOCUMENT_ALREADY_EXISTS` | 409 | DNI o RUC registrado anteriormente. |
| `SKU_ALREADY_EXISTS` | 409 | SKU registrado anteriormente. |
| `CATEGORY_ALREADY_EXISTS` | 409 | Categoria duplicada. |
| `CUSTOMER_INACTIVE` | 409 | Cliente no disponible para nuevas ventas. |
| `PRODUCT_INACTIVE` | 409 | Producto no disponible para nuevas ventas. |
| `CATEGORY_INACTIVE` | 409 | Categoria desactivada. |
| `INSUFFICIENT_STOCK` | 409 | Stock menor que la cantidad solicitada. |
| `IDEMPOTENCY_KEY_REUSED` | 409 | Clave reutilizada con una solicitud diferente. |
| `INTERNAL_ERROR` | 500 | Fallo inesperado sin detalles internos. |

El manejo tecnico de estos errores se implementara en la fase 05.

## 14. Swagger y OpenAPI

Durante la fase 05, FastAPI generara automaticamente:

- `/openapi.json`: especificacion OpenAPI.
- `/docs`: interfaz Swagger UI.
- `/redoc`: documentacion alternativa ReDoc.

La implementacion debe compararse con este documento. Si cambia un contrato, se
actualizan el documento y el codigo en la misma modificacion para evitar que la
documentacion quede desactualizada.

No se mantiene un archivo `openapi.yaml` manual en la primera version. El JSON
generado por FastAPI sera la especificacion ejecutable.

## 15. Trazabilidad con la fase 01

| Requisito | Endpoints relacionados |
| --- | --- |
| RF-01, RF-02 | `/auth/login`, `/auth/me` y permisos globales. |
| RF-03 | `/users`. |
| RF-04 | `/customers`. |
| RF-05 | `/categories` y `/products`. |
| RF-06, RF-07 | `/inventory` y `/inventory/movements`. |
| RF-08, RF-09, RF-10, RF-11 | `/sales`. |
| RF-12 | `GET /sales` y `GET /sales/{id}`. |
| RF-13 | `/dashboard/summary`. |
| RF-14 | Datos conservados por `/sales`. |

## 16. Criterios de aceptacion del contrato

- Todos los requisitos funcionales de la primera version tienen un endpoint.
- Cada endpoint identifica sus permisos.
- Las entradas no permiten que el frontend controle precios o totales.
- Las listas usan paginacion y filtros consistentes.
- Los errores usan una estructura comun y codigos estables.
- Las ventas repetidas se controlan mediante una clave de idempotencia.
- No existen operaciones de borrado para registros con historial.
- Los modulos reservados para fases posteriores no publican endpoints.
- El contrato puede implementarse con FastAPI sin redefinir reglas de negocio.

## 17. Estado de implementacion

La fase 05 implemento la infraestructura comun, `/auth` y `/users`. Los
contratos de clientes, categorias y productos quedaron implementados en la fase
07. La fase 08 completo inventario, movimientos, ventas, detalles y pagos con
control transaccional e idempotencia. El resumen comercial y los modulos
analiticos se completan en sus fases correspondientes. No se publican endpoints
ficticios ni respuestas simuladas desde el backend.
