# Fase 10 - Dashboard Analytics

## Estado

Fase implementada. El Dashboard dejó de consumir los arreglos demostrativos del
frontend y obtiene todos sus indicadores desde la API y las ventas confirmadas
de PostgreSQL/Supabase.

## Alcance implementado

- KPIs de facturación, transacciones, clientes con compra y unidades vendidas.
- Ticket promedio, media aritmética y mediana del importe por venta.
- Ventas por periodo con agrupación diaria, semanal o mensual según el rango.
- Ventas por producto, con facturación, transacciones, unidades y participación.
- Ventas por vendedor, con facturación, transacciones, unidades y participación.
- Distribución y frecuencia de ventas por rangos de ticket.
- Filtros por fecha, sucursal, vendedor y categoría.
- Estados de carga, error y ausencia de ventas.
- Acceso exclusivo para administrador y gerente.

## Fuente y reglas de los cálculos

Solo participan ventas con estado `confirmed` pertenecientes a la empresa del
usuario autenticado. La facturación se calcula desde los subtotales históricos
de `sale_details`; de este modo el filtro de categoría cuenta únicamente las
líneas de esa categoría y no el total completo de una venta mixta.

El ticket promedio y la media representan el promedio del importe filtrado por
transacción. La mediana es el valor central de esos importes. Los productos se
identifican con su nombre histórico almacenado al confirmar la venta.

La primera versión del proyecto opera con una sola empresa y un solo local,
según la fase 01. Por ello el filtro de sucursal ofrece `Sucursal principal` con
el identificador `main`. El contrato queda preparado para ampliar las opciones
cuando el modelo incorpore múltiples locales en una versión posterior.

## API

`GET /api/v1/dashboard/summary`

Parámetros opcionales:

| Parámetro | Descripción |
| --- | --- |
| `date_from` | Fecha inicial inclusiva. Por defecto, primer día del mes actual. |
| `date_to` | Fecha final inclusiva. Por defecto, fecha actual. |
| `branch` | Sucursal; actualmente solo acepta `main`. |
| `seller_id` | Usuario vendedor perteneciente a la empresa. |
| `category_id` | Categoría perteneciente a la empresa. |

El intervalo máximo permitido es de 366 días. La respuesta contiene el periodo
normalizado, filtros aplicados, opciones disponibles, KPIs, series temporales,
desgloses y distribución del ticket.

## Agrupación temporal

- Hasta 31 días: agrupación diaria.
- De 32 a 180 días: agrupación semanal.
- De 181 a 366 días: agrupación mensual.

La API completa los periodos sin ventas con valores en cero para que la gráfica
no oculte interrupciones en la actividad comercial.

## Uso en el frontend

1. Iniciar sesión como administrador o gerente.
2. Abrir `Dashboard`.
3. Seleccionar las fechas y, si corresponde, vendedor o categoría.
4. Presionar `Aplicar filtros`.
5. Revisar KPIs, evolución, productos, vendedores y distribución.

Si no existen ventas en el periodo, los KPIs muestran cero y la interfaz ofrece
un estado vacío en lugar de datos de demostración.

## Verificación

- Pruebas de agregación sobre ventas y detalles reales.
- Pruebas de filtros por vendedor y categoría.
- Prueba del contrato HTTP y autorización por rol.
- Revisión de OpenAPI para `/api/v1/dashboard/summary`.
- Compilación TypeScript, ESLint y Ruff.
