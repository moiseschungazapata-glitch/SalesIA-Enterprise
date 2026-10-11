# Parte 2 — impuestos, descuentos y configuración comercial

## Resultado

Las ventas y pedidos calculan sus importes con una única regla del servidor y guardan el desglose histórico. La configuración se encuentra en **Configuración** y solo puede ser modificada por un administrador.

## Reglas

- IGV configurable por empresa (18 % por defecto).
- El catálogo puede manejar precios que ya incluyen IGV o precios a los que se agrega IGV.
- Descuento por producto y descuento general, aplicados de forma secuencial.
- Límite máximo de descuento configurable (30 % por defecto), validado siempre en el servidor.
- Cada pedido y venta conserva subtotal, descuento, IGV, tasa aplicada y total, aunque la configuración cambie después.
- Al convertir un pedido aprobado, sus descuentos se trasladan a la venta y se vuelve a validar stock y configuración.

## Publicación

1. Ejecutar la migración `20261011_0011_commercial_pricing` en la base de datos.
2. Publicar backend y frontend.
3. Entrar como administrador a **Configuración** y confirmar el IGV, el tratamiento del precio y el descuento máximo.
4. Crear un pedido o una venta de prueba y verificar el desglose en el historial y en el reporte de ventas.
