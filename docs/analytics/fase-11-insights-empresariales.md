# Fase 11 - Insights empresariales

## Estado

Fase implementada. SalesIA transforma los resultados comerciales reales en
observaciones explicables, guarda la evidencia utilizada y conserva cada
ejecución para consultar su historial.

## Alcance implementado

- Reglas determinísticas: una misma entrada produce el mismo hallazgo.
- Observaciones para ventas, productos, vendedores, clientes y estadística.
- Evidencia numérica con métrica, valor, unidad y umbral cuando corresponde.
- Relación verificable entre cada insight, el dataset y el análisis que lo creó.
- Historial permanente: una nueva generación archiva los insights vigentes sin
  borrar las ejecuciones anteriores.
- Filtros visuales por vigencia, categoría y severidad.
- Acceso para administrador y gerente.

## Reglas iniciales

| Código | Interpretación |
| --- | --- |
| `sales.no_activity` | Advierte cuando no existen ventas confirmadas. |
| `sales.period_summary` | Resume transacciones y facturación del periodo. |
| `statistics.ticket_shape` | Compara media y mediana para detectar asimetría. |
| `products.revenue_concentration` | Mide la participación del producto principal. |
| `sellers.revenue_concentration` | Mide la concentración en el vendedor principal. |
| `customers.recurrence_floor` | Calcula un mínimo comprobable de recurrencia. |
| `sales.period_continuity` | Mide cuántos intervalos tuvieron actividad. |

Las reglas no usan IA generativa ni inventan conclusiones. Cada texto se forma
con los valores calculados a partir de las ventas confirmadas del periodo.

## Persistencia y trazabilidad

Cada ejecución crea:

1. Un registro en `datasets` con el periodo y los filtros.
2. La variable agregada `period_revenue`.
3. Una observación por intervalo temporal.
4. Un análisis de tipo `insight` en `statistical_analyses`.
5. Resultados estadísticos básicos y los registros explicables en `insights`.

La evidencia de cada insight contiene el código de regla, categoría, versión del
conjunto de reglas, periodo, dataset, análisis y valores numéricos relevantes.

## API

- `POST /api/v1/insights/generate`: genera y guarda los insights de un periodo.
- `GET /api/v1/insights`: consulta el historial con filtros opcionales por
  categoría, severidad y vigencia.

## Uso en el frontend

1. Iniciar sesión como administrador o gerente.
2. Abrir `Insights` en el menú lateral.
3. Elegir las fechas inicial y final.
4. Presionar `Generar insights`.
5. Revisar la cifra principal, la explicación, el código de regla y los números
   de dataset y análisis.
6. Cambiar `Vigentes` por `Anteriores` o `Todo el historial` para revisar otras
   ejecuciones.

Cuando no hay ventas, el sistema guarda una advertencia comprobable con cero
transacciones. No muestra datos ficticios.

## Verificación

- Pruebas del cálculo y de la evidencia numérica.
- Prueba de persistencia de dataset, observaciones y análisis.
- Prueba de conservación del historial entre ejecuciones.
- Prueba del comportamiento para periodos sin ventas.
- Prueba de permisos y contratos OpenAPI.
- Compilación TypeScript, ESLint y Ruff.
