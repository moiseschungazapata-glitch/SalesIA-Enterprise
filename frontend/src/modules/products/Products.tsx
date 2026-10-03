import { useMemo, useState } from 'react'
import type { UserRole } from '../../app/navigation'
import PageHeader from '../../components/PageHeader'
import { products as initialProducts } from '../../services/mockData'
import type { Product } from '../../types'

interface ProductsProps {
  role: UserRole
}

interface Category {
  id: number
  name: string
  description: string
  status: 'Activa' | 'Inactiva'
}

const initialCategories: Category[] = [
  {
    id: 1,
    name: 'Tecnología',
    description: 'Equipos y dispositivos tecnológicos.',
    status: 'Activa',
  },
  {
    id: 2,
    name: 'Accesorios',
    description: 'Complementos para equipos y estaciones de trabajo.',
    status: 'Activa',
  },
  {
    id: 3,
    name: 'Oficina',
    description: 'Productos para operación administrativa.',
    status: 'Activa',
  },
]

function Products({ role }: ProductsProps) {
  const canManage = role === 'administrator'
  const [productList, setProductList] =
    useState<Product[]>(initialProducts)

  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] =
    useState('Todas')
  const [showForm, setShowForm] = useState(false)
  const [showCategories, setShowCategories] = useState(false)
  const [categoryList, setCategoryList] =
    useState<Category[]>(initialCategories)
  const [categoryName, setCategoryName] = useState('')

  const [form, setForm] = useState({
    name: '',
    category: 'Tecnología',
    price: '',
    stock: '',
  })

  const productCategories = [
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

  const handleAddCategory = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    const name = categoryName.trim()

    if (
      !name ||
      categoryList.some(
        (category) =>
          category.name.toLowerCase() === name.toLowerCase(),
      )
    ) {
      return
    }

    setCategoryList((current) => [
      ...current,
      {
        id: Date.now(),
        name,
        description: 'Categoría creada en el prototipo UX.',
        status: 'Activa',
      },
    ])
    setCategoryName('')
  }

  const toggleCategory = (id: number) => {
    setCategoryList((current) =>
      current.map((category) =>
        category.id === id
          ? {
              ...category,
              status:
                category.status === 'Activa'
                  ? 'Inactiva'
                  : 'Activa',
            }
          : category,
      ),
    )
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="CATÁLOGO"
        title="Productos"
        description={
          canManage
            ? 'Administra productos y categorías; el stock se controla desde inventario.'
            : 'Consulta el catálogo, las categorías y la disponibilidad.'
        }
        action={
          canManage ? (
            <div className="page-actions">
              <button
                type="button"
                className="secondary-button compact"
                onClick={() =>
                  setShowCategories((value) => !value)
                }
              >
                {showCategories
                  ? 'Cerrar categorías'
                  : 'Gestionar categorías'}
              </button>
              <button
                type="button"
                className="primary-button compact"
                onClick={() => setShowForm((value) => !value)}
              >
                {showForm ? 'Cerrar' : '+ Nuevo producto'}
              </button>
            </div>
          ) : undefined
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

      {canManage && showCategories && (
        <section className="panel category-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">CATEGORÍAS</span>
              <h2>Gestión de categorías</h2>
              <p>
                Crea o desactiva categorías sin eliminar su historial.
              </p>
            </div>
          </div>

          <form
            className="inline-entity-form"
            onSubmit={handleAddCategory}
          >
            <label>
              Nombre de la categoría
              <input
                value={categoryName}
                onChange={(event) =>
                  setCategoryName(event.target.value)
                }
                placeholder="Ej. Mobiliario"
              />
            </label>
            <button type="submit" className="primary-button">
              Crear categoría
            </button>
          </form>

          <div className="category-list">
            {categoryList.map((category) => (
              <div className="category-row" key={category.id}>
                <div>
                  <strong>{category.name}</strong>
                  <span>{category.description}</span>
                </div>
                <span
                  className={`status-pill ${
                    category.status === 'Activa'
                      ? 'success'
                      : 'neutral'
                  }`}
                >
                  {category.status}
                </span>
                <button
                  type="button"
                  className="secondary-button compact"
                  onClick={() => toggleCategory(category.id)}
                >
                  {category.status === 'Activa'
                    ? 'Desactivar'
                    : 'Activar'}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {canManage && showForm && (
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
                {categoryList
                  .filter((category) => category.status === 'Activa')
                  .map((category) => (
                    <option key={category.id}>
                      {category.name}
                    </option>
                  ))}
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
            {productCategories.map((category) => (
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
