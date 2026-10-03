# Fase 04 - Diccionario de datos

## 1. Convenciones

- Todas las fechas y horas usan `TIMESTAMP WITH TIME ZONE`.
- La presentacion de fechas utiliza `America/Lima`.
- Los importes comerciales usan `NUMERIC(14,2)` y la moneda inicial es `PEN`.
- `active` representa desactivacion logica; los registros historicos no se
  eliminan desde la aplicacion.
- Las columnas JSONB conservan filtros, parametros, evidencias o resultados
  estructurados que pueden variar entre tipos de analisis.

## 2. Organizacion y acceso

### `companies`

Empresa propietaria de los datos. La primera version crea una sola empresa.

| Columna | Tipo | Regla |
| --- | --- | --- |
| `id` | integer | PK generada |
| `name`, `legal_name` | varchar | Nombre visible y razon social opcional |
| `tax_id` | varchar(20) | Unico y opcional |
| `slug` | varchar(80) | Identificador unico para configuracion |
| `currency` | varchar(3) | `PEN` inicialmente |
| `timezone` | varchar(50) | `America/Lima` inicialmente |
| `active` | boolean | Empresa habilitada |
| `created_at`, `updated_at` | timestamptz | Trazabilidad |

### `roles`

Catalogo global de permisos: `administrator`, `seller` y `manager`.

| Columna | Tipo | Regla |
| --- | --- | --- |
| `id` | integer | PK generada |
| `code` | varchar(40) | Unico; valor usado por la API |
| `name`, `description` | texto | Etiqueta y explicacion |
| `active` | boolean | Rol asignable |
| `created_at`, `updated_at` | timestamptz | Trazabilidad |

### `users`

Usuarios que ingresan a la aplicacion.

| Columna | Tipo | Regla |
| --- | --- | --- |
| `company_id`, `role_id` | integer | FK obligatorias |
| `name` | varchar(160) | Obligatorio |
| `email` | varchar(254) | Unico por empresa, sin distinguir mayusculas |
| `password_hash` | varchar(255) | Solo hash Argon2id; nunca contraseña plana |
| `active` | boolean | Control de acceso |
| `last_login_at` | timestamptz | Ultimo acceso opcional |
| `created_at`, `updated_at` | timestamptz | Trazabilidad |

### `employees`

Ficha laboral opcional para metricas futuras. Puede vincularse uno a uno con un
usuario mediante `user_id`; `employee_code` es unico por empresa.

## 3. Clientes y catalogo

### `customers`

| Columna | Tipo | Regla |
| --- | --- | --- |
| `company_id` | integer | FK obligatoria |
| `customer_type` | varchar(20) | `person` o `company` |
| `document_type` | varchar(10) | `DNI` o `RUC` |
| `document_number` | varchar(20) | Unico por empresa; 8 o 11 digitos segun tipo |
| `name` | varchar(200) | Nombre completo o razon social |
| `phone`, `email`, `address` | texto | Datos de contacto opcionales |
| `active` | boolean | Disponible para nuevas ventas |
| `created_at`, `updated_at` | timestamptz | Trazabilidad |

### `categories`

Nombre unico por empresa sin distinguir mayusculas, descripcion opcional y
estado activo. Una categoria usada no se elimina.

### `products`

| Columna | Tipo | Regla |
| --- | --- | --- |
| `company_id`, `category_id` | integer | FK obligatorias |
| `sku` | varchar(50) | Unico por empresa |
| `name`, `description` | texto | Identidad comercial |
| `unit_price` | numeric(14,2) | Mayor que cero |
| `active` | boolean | Disponible para venta |
| `created_at`, `updated_at` | timestamptz | Trazabilidad |

El stock no se guarda en `products`; se administra exclusivamente en
`inventory` y `inventory_movements`.

## 4. Inventario

### `inventory`

Mantiene una fila unica por producto con `quantity >= 0`. `version` permite
implementar control de concurrencia durante la fase 08.

### `inventory_movements`

| Columna | Tipo | Regla |
| --- | --- | --- |
| `company_id`, `product_id`, `user_id` | integer | FK obligatorias |
| `sale_id` | integer | Obligatoria solo para tipo `sale` |
| `movement_type` | varchar(30) | `initial`, `entry`, `adjustment_in`, `adjustment_out` o `sale` |
| `quantity` | integer | Siempre positiva |
| `stock_before`, `stock_after` | integer | Nunca negativos |
| `reason` | text | Motivo obligatorio |
| `created_at` | timestamptz | Momento inmutable del movimiento |

## 5. Ventas

### `sales`

| Columna | Tipo | Regla |
| --- | --- | --- |
| `company_id`, `customer_id`, `seller_id` | integer | FK obligatorias |
| `number` | varchar(30) | Unico por empresa |
| `idempotency_key` | uuid | Unica por empresa |
| `request_hash` | varchar(64) | Huella para detectar reutilizacion incorrecta |
| `status` | varchar(20) | `confirmed` en la primera version |
| `currency` | varchar(3) | `PEN` |
| `total` | numeric(14,2) | Mayor que cero |
| `confirmed_at`, `created_at`, `updated_at` | timestamptz | Trazabilidad |

### `sale_details`

Una fila por producto dentro de una venta. `quantity > 0`, `unit_price > 0` y
`subtotal` debe ser el precio multiplicado por la cantidad. Guarda los campos
`sku_snapshot`, `product_name_snapshot` y `category_name_snapshot`.

### `payments`

Una venta tiene exactamente un pago en la primera version. El metodo acepta
`cash`, `card` o `bank_transfer`; el estado es `completed` y el importe es
positivo. La igualdad entre pago y total se verifica en el servicio
transaccional de la fase 08 porque involucra dos tablas.

## 6. Analitica

| Tabla | Proposito | Campos principales |
| --- | --- | --- |
| `datasets` | Congelar un conjunto a analizar | empresa, creador, fuente, filtros, periodo |
| `dataset_variables` | Describir cada variable estadistica | nombre, tipo de variable, tipo de dato, unidad |
| `observations` | Conservar cada valor observado | dataset, variable, ordinal, valor numerico o texto |
| `statistical_analyses` | Historial de ejecuciones | tipo, estado, parametros, error, fechas |
| `statistical_results` | Resultados explicitos por metrica | variable, metrica, valor y detalle JSONB |
| `bayes_analyses` | Datos y resultado de Bayes | eventos y cuatro probabilidades entre 0 y 1 |
| `random_variables` | Definicion de variable aleatoria | tipo, distribucion, esperanza y varianza |
| `insights` | Conclusion explicable | titulo, descripcion, severidad y evidencia |

Estas tablas no ejecutan calculos en la fase 04; solamente proporcionan una
estructura consistente para las fases 09 a 11.

## 7. Gobierno

### `reports`

Historial de solicitudes de reportes. Registra tipo, parametros JSONB, estado,
ruta del archivo, error y fechas de generacion.

### `audit_logs`

Bitacora append-only para acciones criticas. Conserva empresa, usuario, accion,
tipo e identificador de entidad, cambios JSONB, identificador de solicitud, IP
y fecha. La captura automatica se implementara en la fase 13.

