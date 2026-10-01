import { products } from '../../services/mockData'

function Products() {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">CATÁLOGO</span>
          <h1>Productos</h1>
          <p>Administra productos, categorías, precios y stock.</p>
        </div>

        <button type="button" className="primary-button compact">
          + Nuevo producto
        </button>
      </div>

      <section className="panel">
        <div className="panel-toolbar">
          <input
            className="search-input"
            placeholder="Buscar producto..."
          />

          <select className="select-input">
            <option>Todas las categorías</option>
            <option>Tecnología</option>
            <option>Accesorios</option>
          </select>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Unidades vendidas</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>
                    <strong>{product.name}</strong>
                  </td>
                  <td>{product.category}</td>
                  <td>
                    S/ {product.price.toLocaleString('es-PE')}
                  </td>
                  <td>{product.stock}</td>
                  <td>{product.sold}</td>
                  <td>
                    <span
                      className={`status-pill ${
                        product.status === 'Disponible'
                          ? 'success'
                          : product.status === 'Stock bajo'
                            ? 'warning'
                            : 'danger'
                      }`}
                    >
                      {product.status}
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

export default Products
