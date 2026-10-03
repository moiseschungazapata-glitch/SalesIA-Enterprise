import { useMemo, useState, type FormEvent } from 'react'
import type { UserRole } from '../../app/navigation'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useCategories, useProducts } from '../../hooks/useCatalog'
import {
  createCategory,
  createProduct,
  updateCategory,
  updateProduct,
  type CategoryListFilters,
} from '../../services/catalog'

interface ProductsProps {
  role: UserRole
}

const pageSize = 10

const emptyProductForm = {
  sku: '',
  name: '',
  description: '',
  categoryId: '',
  price: '',
  initialStock: '0',
}

function Products({ role }: ProductsProps) {
  const canManage = role === 'administrator'
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<number | null>(null)
  const [statusFilter, setStatusFilter] = useState<
    'active' | 'inactive' | ''
  >('')
  const [showForm, setShowForm] = useState(false)
  const [showCategories, setShowCategories] = useState(false)
  const [productForm, setProductForm] = useState(emptyProductForm)
  const [categoryForm, setCategoryForm] = useState({
    name: '',
    description: '',
  })
  const [productFormError, setProductFormError] = useState('')
  const [categoryFormError, setCategoryFormError] = useState('')
  const [feedback, setFeedback] = useState('')
  const [feedbackIsError, setFeedbackIsError] = useState(false)
  const [submittingProduct, setSubmittingProduct] = useState(false)
  const [submittingCategory, setSubmittingCategory] = useState(false)
  const [updatingProductId, setUpdatingProductId] = useState<number | null>(null)
  const [updatingCategoryId, setUpdatingCategoryId] = useState<number | null>(null)

  const categoryFilters = useMemo<CategoryListFilters>(
    () => ({ page: 1, pageSize: 100, search: '', status: '' }),
    [],
  )
  const productsFilters = useMemo(
    () => ({
      page,
      pageSize,
      search,
      categoryId: categoryFilter,
      status: statusFilter,
    }),
    [categoryFilter, page, search, statusFilter],
  )
  const categories = useCategories(categoryFilters)
  const products = useProducts(productsFilters)
  const activeCategories = categories.data.items.filter(
    (category) => category.active,
  )
  const selectedCategoryId =
    productForm.categoryId || String(activeCategories[0]?.id ?? '')
  const totalPages = Math.max(
    1,
    Math.ceil(products.data.total / pageSize),
  )
  const visibleActive = products.data.items.filter(
    (product) => product.active,
  ).length
  const visibleOutOfStock = products.data.items.filter(
    (product) => product.stock === 0,
  ).length
  const visibleUnits = products.data.items.reduce(
    (total, product) => total + product.stock,
    0,
  )

  const showFeedback = (message: string, isError = false) => {
    setFeedback(message)
    setFeedbackIsError(isError)
  }

  const refreshProductsFromFirstPage = () => {
    if (page === 1) products.reload()
    else setPage(1)
  }

  const handleAddCategory = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (categoryForm.name.trim().length < 2) {
      setCategoryFormError('Escribe un nombre de al menos 2 caracteres.')
      return
    }

    setCategoryFormError('')
    setFeedback('')
    setSubmittingCategory(true)
    try {
      await createCategory({
        name: categoryForm.name.trim(),
        description: categoryForm.description.trim() || null,
      })
      setCategoryForm({ name: '', description: '' })
      showFeedback('Categoría creada correctamente en Supabase.')
      categories.reload()
    } catch (requestError) {
      setCategoryFormError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible crear la categoría.',
      )
    } finally {
      setSubmittingCategory(false)
    }
  }

  const toggleCategory = async (categoryId: number, active: boolean) => {
    setUpdatingCategoryId(categoryId)
    setFeedback('')
    try {
      await updateCategory(categoryId, { active: !active })
      showFeedback(
        active
          ? 'Categoría desactivada correctamente.'
          : 'Categoría activada correctamente.',
      )
      categories.reload()
    } catch (requestError) {
      showFeedback(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible actualizar la categoría.',
        true,
      )
    } finally {
      setUpdatingCategoryId(null)
    }
  }

  const handleAddProduct = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const price = Number(productForm.price)
    const initialStock = Number(productForm.initialStock)
    const categoryId = Number(selectedCategoryId)
    if (
      !/^[A-Za-z0-9._-]+$/.test(productForm.sku) ||
      productForm.name.trim().length < 2 ||
      !categoryId ||
      price <= 0 ||
      !Number.isInteger(initialStock) ||
      initialStock < 0
    ) {
      setProductFormError(
        'Completa SKU, nombre, categoría, precio positivo y stock entero no negativo.',
      )
      return
    }

    setProductFormError('')
    setFeedback('')
    setSubmittingProduct(true)
    try {
      await createProduct({
        sku: productForm.sku.trim(),
        name: productForm.name.trim(),
        description: productForm.description.trim() || null,
        category_id: categoryId,
        unit_price: productForm.price,
        initial_stock: initialStock,
      })
      setProductForm(emptyProductForm)
      setShowForm(false)
      showFeedback('Producto y stock inicial guardados correctamente.')
      refreshProductsFromFirstPage()
    } catch (requestError) {
      setProductFormError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible crear el producto.',
      )
    } finally {
      setSubmittingProduct(false)
    }
  }

  const toggleProduct = async (productId: number, active: boolean) => {
    setUpdatingProductId(productId)
    setFeedback('')
    try {
      await updateProduct(productId, { active: !active })
      showFeedback(
        active
          ? 'Producto desactivado correctamente.'
          : 'Producto activado correctamente.',
      )
      products.reload()
    } catch (requestError) {
      showFeedback(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible actualizar el producto.',
        true,
      )
    } finally {
      setUpdatingProductId(null)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="CATÁLOGO"
        title="Productos"
        description={
          canManage
            ? 'Administra productos y categorías reales; el stock se registra con trazabilidad.'
            : 'Consulta el catálogo, las categorías y la disponibilidad.'
        }
        action={
          canManage ? (
            <div className="page-actions">
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => setShowCategories((value) => !value)}
              >
                {showCategories ? 'Cerrar categorías' : 'Gestionar categorías'}
              </button>
              <button
                type="button"
                className="primary-button compact"
                onClick={() => {
                  setShowForm((value) => !value)
                  setProductFormError('')
                }}
                disabled={activeCategories.length === 0}
              >
                {showForm ? 'Cerrar' : '+ Nuevo producto'}
              </button>
            </div>
          ) : undefined
        }
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Resultados</span>
          <strong>{products.data.total}</strong>
        </article>
        <article className="mini-stat">
          <span>Activos visibles</span>
          <strong>{visibleActive}</strong>
        </article>
        <article className="mini-stat">
          <span>Sin stock visibles</span>
          <strong>{visibleOutOfStock}</strong>
        </article>
        <article className="mini-stat">
          <span>Unidades visibles</span>
          <strong>{visibleUnits}</strong>
        </article>
      </section>

      {feedback && (
        <div
          className={feedbackIsError ? 'form-error' : 'form-success'}
          role={feedbackIsError ? 'alert' : 'status'}
        >
          {feedback}
        </div>
      )}

      {canManage && showCategories && (
        <section className="panel category-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">CATEGORÍAS</span>
              <h2>Gestión de categorías</h2>
              <p>Crea o desactiva categorías sin eliminar su historial.</p>
            </div>
          </div>

          <form className="inline-entity-form" onSubmit={handleAddCategory}>
            <label>
              Nombre
              <input
                value={categoryForm.name}
                onChange={(event) =>
                  setCategoryForm({ ...categoryForm, name: event.target.value })
                }
                minLength={2}
                maxLength={120}
                required
                disabled={submittingCategory}
              />
            </label>
            <label>
              Descripción
              <input
                value={categoryForm.description}
                onChange={(event) =>
                  setCategoryForm({
                    ...categoryForm,
                    description: event.target.value,
                  })
                }
                maxLength={500}
                disabled={submittingCategory}
              />
            </label>
            <button
              type="submit"
              className="primary-button"
              disabled={submittingCategory}
            >
              {submittingCategory ? 'Creando…' : 'Crear categoría'}
            </button>
          </form>

          {categoryFormError && (
            <div className="form-error" role="alert">
              {categoryFormError}
            </div>
          )}

          {categories.loading ? (
            <StateMessage type="loading" title="Cargando categorías" />
          ) : categories.error ? (
            <StateMessage
              type="error"
              title="No se pudieron cargar las categorías"
              description={categories.error}
              actionLabel="Reintentar"
              onAction={categories.reload}
            />
          ) : (
            <div className="category-list">
              {categories.data.items.map((category) => (
                <div className="category-row" key={category.id}>
                  <div>
                    <strong>{category.name}</strong>
                    <span>{category.description || 'Sin descripción'}</span>
                  </div>
                  <span
                    className={`status-pill ${
                      category.active ? 'success' : 'neutral'
                    }`}
                  >
                    {category.active ? 'Activa' : 'Inactiva'}
                  </span>
                  <button
                    type="button"
                    className="secondary-button compact"
                    onClick={() =>
                      void toggleCategory(category.id, category.active)
                    }
                    disabled={updatingCategoryId === category.id}
                  >
                    {updatingCategoryId === category.id
                      ? 'Guardando…'
                      : category.active
                        ? 'Desactivar'
                        : 'Activar'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {canManage && showForm && (
        <section className="panel form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">NUEVO REGISTRO</span>
              <h2>Agregar producto</h2>
              <p>El stock inicial genera un movimiento de inventario.</p>
            </div>
          </div>

          <form className="entity-form" onSubmit={handleAddProduct}>
            <label>
              SKU
              <input
                value={productForm.sku}
                onChange={(event) =>
                  setProductForm({ ...productForm, sku: event.target.value })
                }
                maxLength={50}
                placeholder="TEC-001"
                required
                disabled={submittingProduct}
              />
            </label>
            <label>
              Nombre
              <input
                value={productForm.name}
                onChange={(event) =>
                  setProductForm({ ...productForm, name: event.target.value })
                }
                minLength={2}
                maxLength={180}
                required
                disabled={submittingProduct}
              />
            </label>
            <label>
              Categoría
              <select
                value={selectedCategoryId}
                onChange={(event) =>
                  setProductForm({
                    ...productForm,
                    categoryId: event.target.value,
                  })
                }
                required
                disabled={submittingProduct}
              >
                {activeCategories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Precio de venta
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={productForm.price}
                onChange={(event) =>
                  setProductForm({ ...productForm, price: event.target.value })
                }
                required
                disabled={submittingProduct}
              />
            </label>
            <label>
              Stock inicial
              <input
                type="number"
                min="0"
                step="1"
                value={productForm.initialStock}
                onChange={(event) =>
                  setProductForm({
                    ...productForm,
                    initialStock: event.target.value,
                  })
                }
                required
                disabled={submittingProduct}
              />
            </label>
            <label>
              Descripción
              <input
                value={productForm.description}
                onChange={(event) =>
                  setProductForm({
                    ...productForm,
                    description: event.target.value,
                  })
                }
                maxLength={1000}
                disabled={submittingProduct}
              />
            </label>

            {productFormError && (
              <div className="form-error" role="alert">
                {productFormError}
              </div>
            )}

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowForm(false)}
                disabled={submittingProduct}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="primary-button"
                disabled={submittingProduct}
              >
                {submittingProduct ? 'Guardando…' : 'Guardar producto'}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-toolbar products-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
            placeholder="Buscar por SKU, producto o categoría..."
          />
          <select
            className="select-input"
            value={categoryFilter ?? ''}
            onChange={(event) => {
              setCategoryFilter(
                event.target.value ? Number(event.target.value) : null,
              )
              setPage(1)
            }}
          >
            <option value="">Todas las categorías</option>
            {categories.data.items.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          <select
            className="select-input"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(
                event.target.value as 'active' | 'inactive' | '',
              )
              setPage(1)
            }}
          >
            <option value="">Todos los estados</option>
            <option value="active">Activo</option>
            <option value="inactive">Inactivo</option>
          </select>
        </div>

        <div className="results-info">
          Página {products.data.page} de {totalPages} · {products.data.total}{' '}
          resultado(s)
        </div>

        {products.loading ? (
          <StateMessage
            type="loading"
            title="Cargando productos"
            description="Consultando catálogo y existencias en Supabase."
          />
        ) : products.error ? (
          <StateMessage
            type="error"
            title="No se pudieron cargar los productos"
            description={products.error}
            actionLabel="Reintentar"
            onAction={products.reload}
          />
        ) : products.data.items.length === 0 ? (
          <StateMessage
            type="empty"
            title="No se encontraron productos"
            description="Cambia los filtros o registra el primer producto."
          />
        ) : (
          <>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Categoría</th>
                    <th>Precio</th>
                    <th>Stock</th>
                    <th>Estado</th>
                    {canManage && <th>Acción</th>}
                  </tr>
                </thead>
                <tbody>
                  {products.data.items.map((product) => (
                    <tr key={product.id}>
                      <td>
                        <strong>{product.name}</strong>
                        <span className="table-subtitle">{product.sku}</span>
                      </td>
                      <td>{product.category_name}</td>
                      <td>
                        {Number(product.unit_price).toLocaleString('es-PE', {
                          style: 'currency',
                          currency: 'PEN',
                        })}
                      </td>
                      <td>{product.stock}</td>
                      <td>
                        <span
                          className={`status-pill ${
                            product.active ? 'success' : 'neutral'
                          }`}
                        >
                          {product.active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      {canManage && (
                        <td>
                          <button
                            type="button"
                            className="secondary-button compact"
                            onClick={() =>
                              void toggleProduct(product.id, product.active)
                            }
                            disabled={updatingProductId === product.id}
                          >
                            {updatingProductId === product.id
                              ? 'Guardando…'
                              : product.active
                                ? 'Desactivar'
                                : 'Activar'}
                          </button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination-controls">
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => setPage((value) => value - 1)}
                disabled={page <= 1}
              >
                Anterior
              </button>
              <span>Página {page} de {totalPages}</span>
              <button
                type="button"
                className="secondary-button compact"
                onClick={() => setPage((value) => value + 1)}
                disabled={page >= totalPages}
              >
                Siguiente
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  )
}

export default Products
