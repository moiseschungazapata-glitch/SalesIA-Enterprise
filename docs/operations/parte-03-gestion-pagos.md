# Parte 3 — gestión completa de pagos

## Resultado

El sistema permite crear ventas pagadas, con abono parcial o pendientes. Cada venta conserva el total cobrado y el saldo por cobrar, y puede recibir varios pagos hasta completar su total.

## Funciones implementadas

- Módulo independiente **Pagos**.
- Pago total, parcial o pendiente al registrar la venta.
- Múltiples abonos por venta.
- Métodos: efectivo, tarjeta y transferencia bancaria.
- Referencia o número de comprobante opcional.
- Estados automáticos de venta: pendiente, pago parcial, pagada y devuelta.
- Filtros de pagos completados, anulados y devueltos.
- Anulación y devolución con motivo obligatorio.
- Restricción para impedir pagos mayores al saldo.
- Auditoría de registro, anulación y devolución.
- Acceso del vendedor limitado a sus propias ventas y pagos.

## Publicación

1. La migración `20261011_0012_payment_management` debe estar aplicada.
2. Publicar backend y frontend.
3. Crear una venta seleccionando **Dejar pendiente**.
4. Entrar a **Pagos**, registrar dos abonos y comprobar que el saldo llegue a cero.
5. Probar una devolución y revisar la auditoría en Seguridad.
