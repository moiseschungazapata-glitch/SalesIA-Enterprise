# Fase 12 - Reportes

## Estado

Fase implementada y verificada contra Supabase. Los reportes se generan a
partir de datos reales, conservan una copia histórica del resultado y pueden
consultarse, exportarse en CSV o imprimirse desde el navegador.

## Reportes implementados

| Reporte | Contenido principal |
| --- | --- |
| Ventas | Operación, fecha, cliente, vendedor, unidades y total. |
| Estadístico | Análisis, dataset, tipo, estado y resultados calculados. |
| Productos | Categoría, precio, stock, unidades vendidas y facturación. |
| Clientes | Documento, compras, importe acumulado y última compra. |
| Vendedores | Rol, ventas, facturación y última operación. |

Todos aceptan un periodo de hasta 366 días. El periodo predeterminado comprende
desde el primer día del mes actual hasta la fecha presente.

## Historial

Cada generación crea un registro en `reports` con:

- empresa y usuario solicitante;
- tipo y título del reporte;
- fechas utilizadas;
- estado de generación;
- columnas, filas y resumen guardados como una copia histórica;
- fecha de creación y finalización.

La copia guardada evita que un reporte antiguo cambie si posteriormente se
modifican clientes, productos o ventas.

## API

- `POST /api/v1/reports/generate`: genera y guarda un reporte.
- `GET /api/v1/reports`: consulta el historial y filtra por tipo o estado.
- `GET /api/v1/reports/{report_id}`: obtiene la vista completa guardada.
- `GET /api/v1/reports/{report_id}/export?format=csv`: descarga el CSV.

Los endpoints están protegidos para administrador y gerente.

## Uso en el frontend

1. Iniciar sesión como administrador o gerente.
2. Abrir `Reportes` en el menú lateral.
3. Elegir Ventas, Estadístico, Productos, Clientes o Vendedores.
4. Seleccionar el periodo y, si se desea, escribir un título.
5. Presionar `Generar reporte`.
6. Revisar el resumen y la tabla que aparece en la misma pantalla.
7. Usar `Descargar CSV` para exportar o `Imprimir` para abrir la vista imprimible.
8. Desde el historial, usar `Ver` para recuperar la copia guardada o `CSV` para
   descargarla nuevamente.

En la ventana de impresión del navegador también puede elegirse `Guardar como
PDF`, sin requerir una librería adicional en el servidor.

## Verificación

- Pruebas de los cinco tipos de reporte.
- Pruebas de historial, detalle y CSV.
- Pruebas de permisos y contratos OpenAPI.
- Ejecución temporal de los cinco reportes contra Supabase con rollback.
- Compilación TypeScript, ESLint y Ruff.
