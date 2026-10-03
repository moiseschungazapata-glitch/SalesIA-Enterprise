# Fase 07 - Clientes y productos

## 1. Resultado

Clientes, categorias y productos dejaron de utilizar datos locales. El frontend
consume FastAPI y FastAPI persiste los cambios en Supabase PostgreSQL.

## 2. Clientes

Se implemento:

- listado paginado para todos los roles autenticados;
- busqueda por nombre, documento, correo o telefono;
- filtro por estado;
- aislamiento de registros por empresa;
- creacion y activacion/desactivacion exclusiva del administrador;
- personas con DNI de 8 digitos;
- empresas con RUC de 11 digitos;
- documento unico dentro de la empresa;
- contactos opcionales y validacion de correo;
- consulta de ficha individual mediante API.

Endpoints:

```text
GET    /api/v1/customers
POST   /api/v1/customers
GET    /api/v1/customers/{customer_id}
PATCH  /api/v1/customers/{customer_id}
```

## 3. Categorias

Se implemento:

- listado, busqueda y filtro por estado;
- nombre unico sin distinguir mayusculas;
- creacion y activacion/desactivacion por administrador;
- rechazo de categorias inactivas para productos nuevos o reactivados.

Endpoints:

```text
GET    /api/v1/categories
POST   /api/v1/categories
PATCH  /api/v1/categories/{category_id}
```

## 4. Productos y stock inicial

Se implemento:

- listado paginado con categoria y stock actual;
- busqueda por SKU, nombre o categoria;
- filtros por categoria y estado;
- SKU normalizado y unico;
- precio decimal positivo;
- creacion y activacion/desactivacion por administrador;
- consulta de ficha individual mediante API;
- una fila de inventario por producto;
- movimiento `initial` cuando el stock inicial es mayor que cero;
- stock fuera del recurso editable de producto.

Endpoints:

```text
GET    /api/v1/products
POST   /api/v1/products
GET    /api/v1/products/{product_id}
PATCH  /api/v1/products/{product_id}
```

El ajuste posterior de existencias se mantiene reservado para la fase 08 y
siempre debera generar movimientos de inventario.

## 5. Permisos

| Operacion | Administrador | Gerente | Vendedor |
| --- | --- | --- | --- |
| Consultar clientes | Si | Si | Si |
| Gestionar clientes | Si | No | No |
| Consultar categorias y productos | Si | Si | Si |
| Gestionar categorias y productos | Si | No | No |

## 6. Verificacion

Las pruebas automatizadas se ejecutan contra SQLite en memoria y no escriben en
Supabase. Cubren autenticacion, permisos, aislamiento empresarial, DNI/RUC,
duplicados, filtros, categorias inactivas, SKU, stock inicial y movimientos.

Resultado de cierre:

- 20 pruebas aprobadas;
- Ruff sin errores;
- ESLint sin errores;
- compilacion React de produccion correcta;
- esquema Supabase con 22 tablas y RLS verificado;
- consultas reales de clientes, categorias y productos respondieron `200`;
- ninguna escritura de prueba se realizo en Supabase.
