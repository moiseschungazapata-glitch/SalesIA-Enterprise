import { inventory } from '../../services/mockData'

function Inventory() {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">CONTROL OPERATIVO</span>
          <h1>Inventario</h1>
          <p>Seguimiento del stock y movimientos de productos.</p>
        </div>

        <button type="button" className="primary-button compact">
          Registrar movimiento
        </button>
      </div>

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Unidades disponibles</span>
          <strong>52</strong>
        </article>

        <article className="mini-stat">
          <span>Productos críticos</span>
          <strong>2</strong>
        </article>

        <article className="mini-stat">
          <span>Productos agotados</span>
          <strong>1</strong>
        </article>

        <article className="mini-stat">
          <span>Movimientos hoy</span>
          <strong>14</strong>
        </article>
      </section>

      <section className="panel">
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Stock actual</th>
                <th>Mínimo</th>
                <th>Movimiento</th>
                <th>Última actualización</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              {inventory.map((item) => {
                const critical =
                  item.stock <= item.minimum

                return (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.product}</strong>
                    </td>
                    <td>{item.category}</td>
                    <td>{item.stock}</td>
                    <td>{item.minimum}</td>
                    <td
                      className={
                        item.movement.startsWith('+')
                          ? 'success-text'
                          : 'danger-text'
                      }
                    >
                      {item.movement}
                    </td>
                    <td>{item.updated}</td>
                    <td>
                      <span
                        className={`status-pill ${
                          critical
                            ? 'warning'
                            : 'success'
                        }`}
                      >
                        {critical ? 'Revisar' : 'Normal'}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default Inventory
