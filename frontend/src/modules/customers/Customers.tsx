import { customers } from '../../services/mockData'

function Customers() {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">GESTIÓN COMERCIAL</span>
          <h1>Clientes</h1>
          <p>Consulta y administra la cartera de clientes.</p>
        </div>

        <button type="button" className="primary-button compact">
          + Nuevo cliente
        </button>
      </div>

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Total clientes</span>
          <strong>248</strong>
        </article>

        <article className="mini-stat">
          <span>Clientes activos</span>
          <strong>183</strong>
        </article>

        <article className="mini-stat">
          <span>Compradores frecuentes</span>
          <strong>72</strong>
        </article>

        <article className="mini-stat">
          <span>Nuevos este mes</span>
          <strong>19</strong>
        </article>
      </section>

      <section className="panel">
        <div className="panel-toolbar">
          <input
            className="search-input"
            placeholder="Buscar cliente..."
          />

          <select className="select-input">
            <option>Todos los estados</option>
            <option>Activo</option>
            <option>Inactivo</option>
          </select>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Correo</th>
                <th>Teléfono</th>
                <th>Ciudad</th>
                <th>Compras</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td>
                    <strong>{customer.name}</strong>
                  </td>
                  <td>{customer.email}</td>
                  <td>{customer.phone}</td>
                  <td>{customer.city}</td>
                  <td>{customer.purchases}</td>
                  <td>
                    <span
                      className={`status-pill ${
                        customer.status === 'Activo'
                          ? 'success'
                          : 'neutral'
                      }`}
                    >
                      {customer.status}
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

export default Customers
