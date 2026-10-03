import PageHeader from '../../components/PageHeader'
import KpiCard from '../../components/KpiCard'
import {
  inventory,
  sales,
} from '../../services/mockData'
import type {
  PageKey,
  UserRole,
} from '../../app/navigation'

interface DashboardProps {
  role: UserRole
  onNavigate: (page: PageKey) => void
}

function Dashboard({ role, onNavigate }: DashboardProps) {
  const canRegisterSale = role === 'administrator'
  const criticalProducts = inventory.filter(
    (item) => item.stock <= item.minimum,
  )

  const chartValues = [55, 72, 64, 88, 69, 94, 82]
  const chartLabels = [
    'Lun',
    'Mar',
    'Mié',
    'Jue',
    'Vie',
    'Sáb',
    'Dom',
  ]

  return (
    <div className="page">
      <PageHeader
        eyebrow="RESUMEN EJECUTIVO"
        title="Dashboard"
        description="Visión general de la operación comercial de SalesIA."
        action={
          canRegisterSale ? (
            <button
              className="primary-button compact"
              type="button"
              onClick={() => onNavigate('sales')}
            >
              + Nueva venta
            </button>
          ) : undefined
        }
      />

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
              <span className="eyebrow">
                COMPORTAMIENTO
              </span>

              <h2>Ventas por día</h2>

              <p>
                Evolución de las ventas del periodo actual.
              </p>
            </div>

            <span className="panel-period">
              Últimos 7 días
            </span>
          </div>

          <div className="chart chart-improved">
            {chartValues.map((height, index) => (
              <div
                className="chart-column"
                key={chartLabels[index]}
              >
                <div className="chart-value">
                  {height}
                </div>

                <div
                  className="chart-bar"
                  style={{ height: `${height}%` }}
                />

                <span>
                  {chartLabels[index]}
                </span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                INVENTARIO
              </span>

              <h2>Stock crítico</h2>

              <p>
                Productos por debajo del mínimo.
              </p>
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
            {criticalProducts.map((item) => (
              <div
                className="list-row"
                key={item.id}
              >
                <div>
                  <strong>{item.product}</strong>
                  <span>
                    Mínimo: {item.minimum} unidades
                  </span>
                </div>

                <strong className="danger-text">
                  {item.stock} uds.
                </strong>
              </div>
            ))}
          </div>

          <div className="panel-footer">
            <span>
              {criticalProducts.length} productos requieren
              revisión.
            </span>

            <button
              className="secondary-button compact"
              type="button"
              onClick={() => onNavigate('inventory')}
            >
              Revisar
            </button>
          </div>
        </article>
      </section>

      <section className="dashboard-lower-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                ACTIVIDAD
              </span>

              <h2>Ventas recientes</h2>

              <p>
                Últimas operaciones registradas.
              </p>
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
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                ACCESO RÁPIDO
              </span>

              <h2>Módulos</h2>

              <p>
                Accede rápidamente a los módulos operativos.
              </p>
            </div>
          </div>

          <div className="quick-actions">
            <button
              type="button"
              onClick={() => onNavigate('customers')}
            >
              <span>Clientes</span>
              <small>
                {canRegisterSale ? 'Gestionar cartera' : 'Consultar cartera'}
              </small>
              <strong>→</strong>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('products')}
            >
              <span>Productos</span>
              <small>
                {canRegisterSale ? 'Gestionar catálogo' : 'Consultar catálogo'}
              </small>
              <strong>→</strong>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('sales')}
            >
              <span>Ventas</span>
              <small>Historial comercial</small>
              <strong>→</strong>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('inventory')}
            >
              <span>Inventario</span>
              <small>Existencias y movimientos</small>
              <strong>→</strong>
            </button>
          </div>
        </article>
      </section>
    </div>
  )
}

export default Dashboard
