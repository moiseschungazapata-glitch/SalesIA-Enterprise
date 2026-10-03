# Fase 08 - Ventas e inventario

**Estado:** completa y validada el 3 de octubre de 2026.

## 1. Alcance implementado

La fase convierte las pantallas de Ventas e Inventario en modulos reales de la
aplicacion. React consume la API FastAPI y la API usa las tablas ya creadas en
Supabase. Se eliminaron los datos demostrativos de ambos modulos.

### Inventario

- Consulta paginada de existencias por empresa.
- Busqueda por SKU, producto o categoria y filtro por estado.
- Historial inmutable de movimientos para administrador y gerente.
- Registro manual exclusivo del administrador.
- Tipos manuales: stock inicial, entrada, ajuste de entrada y ajuste de salida.
- Validacion de producto activo y bloqueo de salidas sin stock suficiente.
- Las salidas por venta solo pueden ser creadas por el sistema.

### Ventas

- Registro permitido para administrador y vendedor.
- Consulta completa para administrador y gerente.
- El vendedor solo puede listar y abrir sus propias ventas.
- Cliente y productos deben existir, pertenecer a la empresa y estar activos.
- El backend obtiene los precios vigentes; el navegador no envia precios.
- Se registra una venta confirmada, sus detalles y un pago completado.
- Se descuenta stock y se genera un movimiento por cada producto vendido.
- La venta, el pago, los detalles y el inventario se confirman en una sola
  transaccion: si una validacion falla, no se guarda ningun cambio parcial.
- `Idempotency-Key` evita ventas duplicadas ante doble clic o reintento.

## 2. Permisos

| Operacion | Administrador | Vendedor | Gerente |
| --- | --- | --- | --- |
| Consultar existencias | Si | Si | Si |
| Consultar movimientos | Si | No | Si |
| Registrar movimiento manual | Si | No | No |
| Registrar venta | Si | Si | No |
| Consultar todas las ventas | Si | No | Si |
| Consultar ventas propias | Si | Si | Si |

Las restricciones se aplican en el backend. Ocultar un boton en React no se
considera una medida de seguridad.

## 3. Endpoints habilitados

| Metodo | Ruta | Uso |
| --- | --- | --- |
| GET | `/api/v1/inventory` | Consultar existencias |
| GET | `/api/v1/inventory/movements` | Consultar trazabilidad |
| POST | `/api/v1/inventory/movements` | Registrar ajuste autorizado |
| GET | `/api/v1/sales` | Listar ventas permitidas |
| POST | `/api/v1/sales` | Confirmar una venta |
| GET | `/api/v1/sales/{id}` | Consultar el detalle de una venta |

## 4. Integridad de una venta

El registro sigue este orden dentro de una sola transaccion:

1. Valida clave de idempotencia, cliente y productos.
2. Bloquea las filas de inventario mientras calcula la operacion.
3. Comprueba existencias suficientes para todos los productos.
4. Calcula precios, subtotales y total con los valores de la base.
5. Crea cabecera, detalles y pago.
6. Descuenta cada existencia y registra su movimiento relacionado.
7. Confirma todos los cambios juntos.

El numero se genera despues de obtener el identificador de la venta con el
formato `V-000001`. No existen edicion ni eliminacion de ventas confirmadas.

## 5. Interfaz React

- Ventas carga clientes activos, productos activos con stock e historial real.
- El carrito muestra un estimado, pero la API vuelve a calcular el total.
- El boton se bloquea durante el envio y cada operacion usa una clave UUID.
- Inventario presenta existencias reales y deja de mostrar umbrales ficticios.
- Los mensajes de carga, error y exito se muestran dentro de cada modulo.
- Al confirmar una venta o movimiento, las listas se vuelven a consultar.

## 6. Verificacion

La suite aislada de fase 08 comprueba:

- permisos de los tres roles;
- entradas y ajustes de inventario;
- rechazo de stock insuficiente y productos inactivos;
- precio calculado por el servidor;
- persistencia coordinada de venta, detalles, pago y movimientos;
- rollback completo de una venta invalida;
- idempotencia con repeticion identica y conflicto por contenido distinto;
- aislamiento de ventas por vendedor;
- publicacion de los seis endpoints en OpenAPI.

Las pruebas automatizadas usan SQLite en memoria y no escriben datos de prueba
en Supabase. La comprobacion contra Supabase se limita a lecturas autenticadas.
Puede repetirse con `python scripts/verify_phase08_readonly.py` desde `backend`.

## 7. Cierre y limite

La fase 08 queda cerrada con los flujos operativos de venta e inventario. El
Dashboard y los modulos de estadistica, probabilidad y analitica todavia pueden
mostrar datos demostrativos porque pertenecen a las siguientes fases. La fase 09
continua con estadistica descriptiva y probabilidad sobre datos preparados.
