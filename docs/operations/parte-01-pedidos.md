# Parte 01 - Pedidos

## Estado

Implementada como ampliación de la fase 08 del Plan Integral de Desarrollo.

## Flujo

`Cliente -> Pedido -> Aprobación -> Venta -> Pago -> Inventario`

Un pedido registra precios históricos y cantidades, pero no modifica existencias.
Al convertirlo, el backend vuelve a validar cliente, productos, precios y stock;
después crea la venta, el pago y los movimientos de inventario en la misma
transacción. El pedido conserva el enlace a la venta resultante.

## Estados

- `pending`: editable y pendiente de aprobación.
- `approved`: autorizado para convertirse en venta.
- `cancelled`: cierre sin venta; no puede editarse ni convertirse.
- `converted`: convertido y enlazado con una venta confirmada.
- `draft`: reservado por el contrato para una futura persistencia automática.

## Permisos

- Administrador y vendedor: crear, editar sus pedidos cuando corresponda,
  aprobar, cancelar y convertir.
- Vendedor: solo consulta sus propios pedidos.
- Gerente: consulta todos los pedidos, sin modificarlos.

## API

- `GET /api/v1/orders`
- `POST /api/v1/orders`
- `GET /api/v1/orders/{id}`
- `PATCH /api/v1/orders/{id}`
- `POST /api/v1/orders/{id}/status`
- `POST /api/v1/orders/{id}/convert`

La conversión requiere `Idempotency-Key`, igual que el alta directa de ventas.
Todas las modificaciones generan auditoría.

## Base de datos

La migración `20261011_0010` crea `orders` y `order_details`, sus restricciones,
índices, relaciones y protección RLS sin políticas públicas.

## Criterios verificados

- Crear y editar un pedido sin descontar stock.
- Aprobar o cancelar mediante transiciones válidas.
- Rechazar la creación por parte del gerente.
- Aislar los pedidos del vendedor.
- Convertir un pedido aprobado en venta, pago y salida de inventario.
- Impedir una segunda conversión.
- Conservar el número del pedido y la referencia a la venta.
