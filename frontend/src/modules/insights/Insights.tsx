import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import { insights as initialInsights } from '../../services/mockData'
import type { Insight } from '../../types'

type InsightFilter =
  | 'Todos'
  | 'Ventas'
  | 'Clientes'
  | 'Inventario'
  | 'Productos'

function Insights() {
  const [insightList] =
    useState<Insight[]>(initialInsights)

  const [filter, setFilter] =
    useState<InsightFilter>('Todos')

  const filteredInsights = useMemo(() => {
    if (filter === 'Todos') {
      return insightList
    }

    return insightList.filter(
      (insight) =>
        insight.category === filter,
    )
  }, [filter, insightList])

  const positive = insightList.filter(
    (insight) => insight.type === 'positive',
  ).length

  const warnings = insightList.filter(
    (insight) => insight.type === 'warning',
  ).length

  return (
    <div className="page">
      <PageHeader
        eyebrow="RESULTADOS ANALÍTICOS"
        title="Insights"
        description="Observaciones generadas a partir de los resultados comerciales y estadísticos."
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Total insights</span>
          <strong>{insightList.length}</strong>
        </article>

        <article className="mini-stat">
          <span>Resultados positivos</span>
          <strong>{positive}</strong>
        </article>

        <article className="mini-stat">
          <span>Alertas</span>
          <strong>{warnings}</strong>
        </article>

        <article className="mini-stat">
          <span>Categorías</span>
          <strong>4</strong>
        </article>
      </section>

      <section className="panel">
        <div className="insight-toolbar">
          <div>
            <span className="eyebrow">
              FILTRAR RESULTADOS
            </span>

            <h2>Observaciones del análisis</h2>
          </div>

          <div className="insight-filters">
            {[
              'Todos',
              'Ventas',
              'Clientes',
              'Inventario',
              'Productos',
            ].map((item) => (
              <button
                key={item}
                type="button"
                className={
                  filter === item
                    ? 'insight-filter active'
                    : 'insight-filter'
                }
                onClick={() =>
                  setFilter(
                    item as InsightFilter,
                  )
                }
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="insight-grid">
        {filteredInsights.map((insight) => (
          <article
            key={insight.id}
            className={`insight-card ${insight.type}`}
          >
            <div className="insight-top">
              <span className="status-pill neutral">
                {insight.category}
              </span>

              <strong>{insight.metric}</strong>
            </div>

            <h2>{insight.title}</h2>

            <p>{insight.description}</p>

            <div className="insight-indicator">
              <span
                className={`insight-dot ${insight.type}`}
              />

              <span>
                {insight.type === 'positive'
                  ? 'Comportamiento favorable'
                  : insight.type === 'warning'
                    ? 'Requiere atención'
                    : 'Información relevante'}
              </span>
            </div>
          </article>
        ))}
      </section>

      {filteredInsights.length === 0 && (
        <section className="empty-state">
          No hay insights para el filtro seleccionado.
        </section>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">
              INTERPRETACIÓN
            </span>

            <h2>Resumen de resultados</h2>

            <p>
              Esta capa presenta observaciones que posteriormente
              podrán generarse desde el backend a partir de los
              análisis estadísticos.
            </p>
          </div>
        </div>

        <div className="insight-summary">
          <div>
            <span>Ventas</span>
            <strong>
              Mayor participación en Tecnología
            </strong>
          </div>

          <div>
            <span>Inventario</span>
            <strong>
              Existen productos bajo el mínimo
            </strong>
          </div>

          <div>
            <span>Clientes</span>
            <strong>
              Se observan clientes recurrentes
            </strong>
          </div>

          <div>
            <span>Estadística</span>
            <strong>
              Media y mediana disponibles
            </strong>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Insights
