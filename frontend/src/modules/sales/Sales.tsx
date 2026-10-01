import { sales } from '../../services/mockData'

function Sales() {
  const total = sales.reduce(
    (sum, sale) => sum + sale.total,
    0,
  )

  const average = total / sales.length

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">OPERACIÓN COMERCIAL</span>
          <h1>Ventas</h1>
          <p>Control de operaciones, pagos y tickets.</p>
        </div>

        <button type="button" className="primary-button compact">
          + Registrar venta
        </button>
      </div>

      <section className="kpi-grid">
        <Kpi label="Ventas registradas" value="248" />
        <Kpi label="Ingresos" value="S/ 84,520" />
        <Kpi
          label="Ticket promedio"
          value={`S/ ${average.toFixed(0)}`}
        />
        <Kpi label="Pagos pendientes" value="7" />
      </section>

      <section className="panel">
        <div className="panel-toolbar">
          <input
            className="search-input"
            placeholder="Buscar venta..."
          />

          <button type="button" className="secondary-button">
            Exportar
          </button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Venta</th>
                <th>Cliente</th>
                <th>Vendedor</th>
                <th>Fecha</th>
                <th>Items</th>
                <th>Total</th>
                <th>Pago</th>
              </tr>
            </thead>

            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>
                    <strong>{sale.id}</strong>
                  </td>
                  <td>{sale.customer}</td>
                  <td>{sale.seller}</td>
                  <td>{sale.date}</td>
                  <td>{sale.items}</td>
                  <td>
                    S/ {sale.total.toLocaleString('es-PE')}
                  </td>
                  <td>
                    <span
                      className={`status-pill ${
                        sale.payment === 'Completado'
                          ? 'success'
                          : 'warning'
                      }`}
                    >
                      {sale.payment}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function Kpi({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <article className="kpi-card">
      <div className="kpi-top">
        <span>{label}</span>
      </div>
      <strong className="kpi-value">{value}</strong>
    </article>
  )
}

export default Sales
