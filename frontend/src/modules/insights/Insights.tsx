import { insights } from '../../services/mockData'

function Insights() {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">RESULTADOS ANALÍTICOS</span>
          <h1>Insights</h1>
          <p>
            Observaciones derivadas de los resultados
            estadísticos y comerciales.
          </p>
        </div>
      </div>

      <section className="insight-grid">
        {insights.map((insight) => (
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

            <div className="insight-footer">
              Generado a partir del análisis disponible
            </div>
          </article>
        ))}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Resumen de hallazgos</h2>
            <p>
              Los insights sirven como capa interpretativa
              sobre los resultados analíticos.
            </p>
          </div>
        </div>

        <div className="summary-box">
          <strong>
            4 observaciones disponibles
          </strong>

          <span>
            Los resultados se muestran actualmente con
            información de demostración.
          </span>
        </div>
      </section>
    </div>
  )
}

export default Insights
