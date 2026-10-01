import KpiCard from '../../components/KpiCard'
import {
  inventory,
  sales,
} from '../../services/mockData'

interface DashboardProps {
  onNavigate: (page: any) => void
}

function Dashboard({ onNavigate }: DashboardProps) {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">RESUMEN EJECUTIVO</span>
          <h1>Dashboard</h1>
          <p>
            Visión general de la operación comercial.
          </p>
        </div>

        <button
          className="primary-button compact"
          type="button"
          onClick={() => onNavigate('sales')}
        >
          Nueva venta
        </button>
      </div>

      <section className="kpi-grid">
        <KpiCard
          label="Ventas del periodo"
          value="S/ 84,520"
          change="+12.8%"
          detail="vs. periodo anterior"
        />

        <KpiCard
          label="Transacciones"
          value="248"
          change="+8.4%"
          detail="ventas registradas"
        />

        <KpiCard
          label="Clientes activos"
          value="183"
          change="+5.2%"
          detail="clientes con actividad"
        />

        <KpiCard
          label="Ticket promedio"
          value="S/ 341"
          change="+3.7%"
          detail="promedio de ventas"
        />
      </section>

      <section className="dashboard-grid">
        <article className="panel panel-large">
          <div className="panel-header">
            <div>
              <h2>Rendimiento de ventas</h2>
              <p>Ventas registradas durante el periodo.</p>
            </div>

            <span className="panel-period">
              Últimos 7 días
            </span>
          </div>

          <div className="chart">
            {[55, 72, 64, 88, 69, 94, 82].map(
              (height, index) => (
                <div className="chart-column" key={index}>
                  <div
                    className="chart-bar"
                    style={{ height: `${height}%` }}
                  />
                  <span>
                    {[
                      'Lun',
                      'Mar',
                      'Mié',
                      'Jue',
                      'Vie',
                      'Sáb',
                      'Dom',
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
              <h2>Stock crítico</h2>
              <p>Productos debajo del mínimo.</p>
            </div>

            <button
              className="text-button"
              type="button"
              onClick={() => onNavigate('inventory')}
            >
              Ver todo
            </button>
          </div>

          <div className="list">
            {inventory
              .filter((item) => item.stock <= item.minimum)
              .map((item) => (
                <div className="list-row" key={item.id}>
                  <div>
                    <strong>{item.product}</strong>
                    <span>{item.category}</span>
                  </div>

                  <strong className="danger-text">
                    {item.stock} uds.
                  </strong>
                </div>
              ))}
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Ventas recientes</h2>
            <p>Últimas operaciones registradas.</p>
          </div>

          <button
            className="text-button"
            type="button"
            onClick={() => onNavigate('sales')}
          >
            Ver ventas
          </button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Vendedor</th>
                <th>Fecha</th>
                <th>Total</th>
                <th>Pago</th>
              </tr>
            </thead>

            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.id}</td>
                  <td>{sale.customer}</td>
                  <td>{sale.seller}</td>
                  <td>{sale.date}</td>
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

export default Dashboard
