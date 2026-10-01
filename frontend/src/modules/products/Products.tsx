import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import { products as initialProducts } from '../../services/mockData'
import type { Product } from '../../types'

function Products() {
  const [productList, setProductList] =
    useState<Product[]>(initialProducts)

  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] =
    useState('Todas')
  const [showForm, setShowForm] = useState(false)

  const [form, setForm] = useState({
    name: '',
    category: 'Tecnología',
    price: '',
    stock: '',
  })

  const categories = [
    ...new Set(productList.map((product) => product.category)),
  ]

  const filteredProducts = useMemo(() => {
    return productList.filter((product) => {
      const matchesSearch =
        product.name
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        product.category
          .toLowerCase()
          .includes(search.toLowerCase())

      const matchesCategory =
        categoryFilter === 'Todas' ||
        product.category === categoryFilter

      return matchesSearch && matchesCategory
    })
  }, [productList, search, categoryFilter])

  const lowStock = productList.filter(
    (product) =>
      product.stock > 0 && product.stock <= 8,
  ).length

  const outOfStock = productList.filter(
    (product) => product.stock === 0,
  ).length

  const handleAddProduct = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    const price = Number(form.price)
    const stock = Number(form.stock)

    if (
      !form.name.trim() ||
      !form.category.trim() ||
      !form.price ||
      !form.stock ||
      price <= 0 ||
      stock < 0
    ) {
      return
    }

    const newProduct: Product = {
      id: Date.now(),
      name: form.name,
      category: form.category,
      price,
      stock,
      sold: 0,
      status:
        stock === 0
          ? 'Agotado'
          : stock <= 8
            ? 'Stock bajo'
            : 'Disponible',
    }

    setProductList((current) => [
      newProduct,
      ...current,
    ])

    setForm({
      name: '',
      category: 'Tecnología',
      price: '',
      stock: '',
    })

    setShowForm(false)
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="CATÁLOGO"
        title="Productos"
        description="Administra productos, categorías, precios y stock."
        action={
          <button
            type="button"
            className="primary-button compact"
            onClick={() => setShowForm((value) => !value)}
          >
            {showForm ? 'Cerrar' : '+ Nuevo producto'}
          </button>
        }
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Total productos</span>
          <strong>{productList.length}</strong>
        </article>

        <article className="mini-stat">
          <span>Stock bajo</span>
          <strong>{lowStock}</strong>
        </article>

        <article className="mini-stat">
          <span>Agotados</span>
          <strong>{outOfStock}</strong>
        </article>

        <article className="mini-stat">
          <span>Unidades vendidas</span>
          <strong>
            {productList
              .reduce(
                (total, product) => total + product.sold,
                0,
              )
              .toLocaleString('es-PE')}
          </strong>
        </article>
      </section>

      {showForm && (
        <section className="panel form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                NUEVO REGISTRO
              </span>
              <h2>Agregar producto</h2>
              <p>
                Completa los datos básicos del producto.
              </p>
            </div>
          </div>

          <form
            className="entity-form"
            onSubmit={handleAddProduct}
          >
            <label>
              Nombre
              <input
                value={form.name}
                onChange={(event) =>
                  setForm({
                    ...form,
                    name: event.target.value,
                  })
                }
                placeholder="Nombre del producto"
              />
            </label>

            <label>
              Categoría
              <select
                value={form.category}
                onChange={(event) =>
                  setForm({
                    ...form,
                    category: event.target.value,
                  })
                }
              >
                <option>Tecnología</option>
                <option>Accesorios</option>
                <option>Oficina</option>
                <option>Otros</option>
              </select>
            </label>

            <label>
              Precio
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={(event) =>
                  setForm({
                    ...form,
                    price: event.target.value,
                  })
                }
                placeholder="0.00"
              />
            </label>

            <label>
              Stock inicial
              <input
                type="number"
                min="0"
                value={form.stock}
                onChange={(event) =>
                  setForm({
                    ...form,
                    stock: event.target.value,
                  })
                }
                placeholder="0"
              />
            </label>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowForm(false)}
              >
                Cancelar
              </button>

              <button
                type="submit"
                className="primary-button"
              >
                Guardar producto
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Buscar producto o categoría..."
          />

          <select
            className="select-input"
            value={categoryFilter}
            onChange={(event) =>
              setCategoryFilter(event.target.value)
            }
          >
            <option>Todas</option>
            {categories.map((category) => (
              <option key={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="results-info">
          Mostrando {filteredProducts.length} de{' '}
          {productList.length} productos
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Vendidos</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              {filteredProducts.map((product) => (
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

          {filteredProducts.length === 0 && (
            <div className="empty-state">
              No se encontraron productos.
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default Products
