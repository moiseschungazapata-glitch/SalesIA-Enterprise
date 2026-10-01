function Analytics() {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">MOTOR ANALÍTICO</span>
          <h1>Analytics</h1>
          <p>
            Análisis estadístico de los datos comerciales.
          </p>
        </div>

        <button type="button" className="secondary-button">
          Actualizar análisis
        </button>
      </div>

      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-top">
            <span>Media de venta</span>
          </div>
          <strong className="kpi-value">S/ 341.20</strong>
          <span className="kpi-detail">
            promedio de la muestra
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Mediana</span>
          </div>
          <strong className="kpi-value">S/ 298.00</strong>
          <span className="kpi-detail">
            valor central de la muestra
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Observaciones</span>
          </div>
          <strong className="kpi-value">248</strong>
          <span className="kpi-detail">
            registros analizados
          </span>
        </article>

        <article className="kpi-card">
          <div className="kpi-top">
            <span>Variables</span>
          </div>
          <strong className="kpi-value">12</strong>
          <span className="kpi-detail">
            variables disponibles
          </span>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel panel-large">
          <div className="panel-header">
            <div>
              <h2>Ventas por periodo</h2>
              <p>Comparación del comportamiento comercial.</p>
            </div>
          </div>

          <div className="chart">
            {[48, 62, 55, 70, 84, 76, 92, 81].map(
              (height, index) => (
                <div className="chart-column" key={index}>
                  <div
                    className="chart-bar"
                    style={{ height: `${height}%` }}
                  />
                  <span>
                    {[
                      'Ago',
                      'Ago',
                      'Sep',
                      'Sep',
                      'Sep',
                      'Oct',
                      'Oct',
                      'Oct',
                    ][index]}
                  </span>
                </div>
              ),
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <h2>Variables estadísticas</h2>
              <p>Variables disponibles para análisis.</p>
            </div>
          </div>

          <div className="variable-list">
            {[
              ['total_venta', 'Cuantitativa'],
              ['cantidad_items', 'Cuantitativa'],
              ['ciudad', 'Cualitativa'],
              ['categoria', 'Cualitativa'],
              ['frecuencia_compra', 'Cuantitativa'],
            ].map(([name, type]) => (
              <div className="variable-row" key={name}>
                <strong>{name}</strong>
                <span>{type}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="analytics-cards">
        <article className="analysis-card">
          <span className="eyebrow">MEDIA</span>
          <h3>Promedio de ventas</h3>
          <strong>S/ 341.20</strong>
          <p>
            Valor obtenido a partir del conjunto de
            observaciones disponibles.
          </p>
        </article>

        <article className="analysis-card">
          <span className="eyebrow">MEDIANA</span>
          <h3>Valor central</h3>
          <strong>S/ 298.00</strong>
          <p>
            Permite observar el centro de los datos con
            menor influencia de valores extremos.
          </p>
        </article>

        <article className="analysis-card">
          <span className="eyebrow">DISTRIBUCIÓN</span>
          <h3>Comportamiento</h3>
          <strong>Moderado</strong>
          <p>
            La distribución muestra concentración en los
            valores intermedios.
          </p>
        </article>
      </section>
    </div>
  )
}

export default Analytics
