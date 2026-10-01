function Reports() {
  const reportCards = [
    {
      title: 'Resumen ejecutivo',
      description:
        'Indicadores generales de ventas, clientes y operación.',
      type: 'Comercial',
    },
    {
      title: 'Análisis de ventas',
      description:
        'Resultados estadísticos sobre ventas y ticket promedio.',
      type: 'Analytics',
    },
    {
      title: 'Inventario',
      description:
        'Situación del stock y productos críticos.',
      type: 'Inventario',
    },
    {
      title: 'Probabilidad',
      description:
        'Resultados de eventos probabilísticos y Bayes.',
      type: 'Estadístico',
    },
  ]

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">DOCUMENTACIÓN</span>
          <h1>Reportes</h1>
          <p>
            Consulta y prepara reportes de la información
            empresarial.
          </p>
        </div>
      </div>

      <section className="report-grid">
        {reportCards.map((report) => (
          <article className="report-card" key={report.title}>
            <div className="report-icon">R</div>

            <span className="eyebrow">
              {report.type}
            </span>

            <h2>{report.title}</h2>

            <p>{report.description}</p>

            <div className="report-actions">
              <button
                type="button"
                className="secondary-button"
              >
                Vista previa
              </button>

              <button
                type="button"
                className="primary-button compact"
                onClick={() =>
                  alert(
                    'El reporte quedará conectado al backend en la siguiente etapa.',
                  )
                }
              >
                Generar
              </button>
            </div>
          </article>
        ))}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Historial de reportes</h2>
            <p>Reportes preparados recientemente.</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Reporte</th>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>
                  <strong>Resumen comercial septiembre</strong>
                </td>
                <td>Comercial</td>
                <td>30/09/2026</td>
                <td>
                  <span className="status-pill success">
                    Disponible
                  </span>
                </td>
              </tr>

              <tr>
                <td>
                  <strong>Análisis estadístico mensual</strong>
                </td>
                <td>Analytics</td>
                <td>30/09/2026</td>
                <td>
                  <span className="status-pill success">
                    Disponible
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default Reports
