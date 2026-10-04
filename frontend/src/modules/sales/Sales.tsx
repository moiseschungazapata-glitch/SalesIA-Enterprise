import { useMemo, useState } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useProducts } from '../../hooks/useCatalog'
import { useCustomers } from '../../hooks/useCustomers'
import { useSales } from '../../hooks/useOperations'
import { createSale } from '../../services/operations'
import type { PaymentMethod, ProductRecord } from '../../types/api'

interface SalesProps {
  role: UserRole
}

interface CartItem {
  product: ProductRecord
  quantity: number
}

const paymentLabels: Record<PaymentMethod, string> = {
  cash: 'Efectivo',
  card: 'Tarjeta',
  bank_transfer: 'Transferencia',
}

function money(value: number | string) {
  return Number(value).toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short', timeStyle: 'short',
  }).format(new Date(value))
}

function Sales({ role }: SalesProps) {
  const canRegister = role !== 'manager'
  const [showForm, setShowForm] = useState(false)
  const [search, setSearch] = useState('')
  const sales = useSales({ page: 1, pageSize: 100, number: search })
  const customers = useCustomers({
    page: 1, pageSize: 100, search: '', status: 'active',
  })
  const products = useProducts({
    page: 1,
    pageSize: 100,
    search: '',
    categoryId: null,
    status: 'active',
  })
  const [selectedCustomer, setSelectedCustomer] = useState('')
  const [selectedProduct, setSelectedProduct] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('cash')
  const [cart, setCart] = useState<CartItem[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [idempotencyKey, setIdempotencyKey] = useState(() => crypto.randomUUID())

  const selectedProductData = products.data.items.find(
    (product) => product.id === Number(selectedProduct),
  )
  const total = useMemo(
    () => cart.reduce(
      (sum, item) => sum + Number(item.product.unit_price) * item.quantity, 0,
    ),
    [cart],
  )
  const salesTotal = sales.data.items.reduce(
    (sum, sale) => sum + Number(sale.total), 0,
  )
  const averageTicket = sales.data.total ? salesTotal / sales.data.total : 0

  const changeRequest = () => setIdempotencyKey(crypto.randomUUID())

  const addToCart = () => {
    setError('')
    setSuccess('')
    const requested = Number(quantity)
    if (!selectedProductData || requested < 1) {
      setError('Selecciona un producto y una cantidad válida.')
      return
    }
    const existing = cart.find((item) => item.product.id === selectedProductData.id)
    const newQuantity = requested + (existing?.quantity ?? 0)
    if (newQuantity > selectedProductData.stock) {
      setError(`Solo hay ${selectedProductData.stock} unidades disponibles.`)
      return
    }
    setCart((current) => existing
      ? current.map((item) => item.product.id === selectedProductData.id
        ? { ...item, quantity: newQuantity }
        : item)
      : [...current, { product: selectedProductData, quantity: requested }])
    setSelectedProduct('')
    setQuantity('1')
    changeRequest()
  }

  const removeFromCart = (productId: number) => {
    setCart((current) => current.filter((item) => item.product.id !== productId))
    changeRequest()
  }

  const registerSale = async () => {
    setError('')
    setSuccess('')
    if (!selectedCustomer || cart.length === 0) {
      setError('Selecciona un cliente y agrega al menos un producto.')
      return
    }
    setSaving(true)
    try {
      const created = await createSale({
        customer_id: Number(selectedCustomer),
        payment_method: paymentMethod,
        items: cart.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
        })),
      }, idempotencyKey)
      setSuccess(`${created.number} confirmada por S/ ${money(created.total)}.`)
      setShowForm(false)
      setCart([])
      setSelectedCustomer('')
      setPaymentMethod('cash')
      setIdempotencyKey(crypto.randomUUID())
      sales.reload()
      products.reload()
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'No se pudo registrar la venta.',
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="OPERACIÓN COMERCIAL"
        title="Ventas"
        description="Ventas confirmadas con pago y descuento automático de inventario."
        action={canRegister ? (
          <button
            type="button"
            className="primary-button compact"
            onClick={() => {
              setShowForm(true)
              setError('')
              setSuccess('')
            }}
          >
            + Nueva venta
          </button>
        ) : undefined}
      />

      <section className="kpi-grid">
        <article className="kpi-card"><div className="kpi-top"><span>Ventas registradas</span></div><strong className="kpi-value">{sales.data.total}</strong><span className="kpi-detail">operaciones visibles para tu perfil</span></article>
        <article className="kpi-card"><div className="kpi-top"><span>Ingresos mostrados</span></div><strong className="kpi-value">S/ {money(salesTotal)}</strong><span className="kpi-detail">total confirmado</span></article>
        <article className="kpi-card"><div className="kpi-top"><span>Ticket promedio</span></div><strong className="kpi-value">S/ {money(averageTicket)}</strong><span className="kpi-detail">promedio por venta</span></article>
        <article className="kpi-card"><div className="kpi-top"><span>Estado</span></div><strong className="kpi-value">100%</strong><span className="kpi-detail">pagos completados</span></article>
      </section>

      {success && <StateMessage type="success" title="Venta registrada" description={success} />}

      {canRegister && showForm && (
        <FormModal
          eyebrow="NUEVA OPERACIÓN"
          title="Registrar venta"
          description="El precio, el stock y el total son verificados por el servidor."
          onClose={() => setShowForm(false)}
          closeDisabled={saving}
          size="wide"
        >
          <div className="sale-modal-content">
            {error && <StateMessage type="error" title="No se pudo completar la operación" description={error} />}
            <div className="sale-form">
              <label>
                Cliente
                <select
                  value={selectedCustomer}
                  onChange={(event) => {
                    setSelectedCustomer(event.target.value)
                    changeRequest()
                  }}
                  disabled={customers.loading}
                >
                  <option value="">Seleccionar cliente</option>
                  {customers.data.items.map((customer) => (
                    <option key={customer.id} value={customer.id}>{customer.name} · {customer.document_number}</option>
                  ))}
                </select>
              </label>
              <label>
                Producto
                <select value={selectedProduct} onChange={(event) => setSelectedProduct(event.target.value)} disabled={products.loading}>
                  <option value="">Seleccionar producto</option>
                  {products.data.items.filter((product) => product.stock > 0).map((product) => (
                    <option key={product.id} value={product.id}>{product.sku} · {product.name} · S/ {money(product.unit_price)}</option>
                  ))}
                </select>
              </label>
              <label>
                Cantidad
                <input type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} />
              </label>
              <div className="sale-add-row">
                <div className="selected-product-info">
                  <strong>{selectedProductData?.name ?? 'Selecciona un producto'}</strong>
                  <span>{selectedProductData ? `Stock disponible: ${selectedProductData.stock}` : 'Aquí aparecerá su disponibilidad.'}</span>
                </div>
                <button type="button" className="primary-button" onClick={addToCart}>Agregar</button>
              </div>
            </div>

            <div className="cart-section">
              <div className="cart-header"><div><strong>Productos de la venta</strong><span>{cart.length} productos distintos</span></div></div>
              {cart.length === 0 ? (
                <div className="empty-state cart-empty">Agrega al menos un producto.</div>
              ) : (
                <div className="cart-list">
                  {cart.map((item) => (
                    <div className="cart-row" key={item.product.id}>
                      <div><strong>{item.product.name}</strong><span>{item.quantity} × S/ {money(item.product.unit_price)}</span></div>
                      <strong>S/ {money(Number(item.product.unit_price) * item.quantity)}</strong>
                      <button type="button" className="remove-button" onClick={() => removeFromCart(item.product.id)}>Quitar</button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="sale-summary">
              <div><span>Total estimado</span><strong>S/ {money(total)}</strong></div>
              <label>
                Método de pago
                <select
                  value={paymentMethod}
                  onChange={(event) => {
                    setPaymentMethod(event.target.value as PaymentMethod)
                    changeRequest()
                  }}
                >
                  <option value="cash">Efectivo</option>
                  <option value="card">Tarjeta</option>
                  <option value="bank_transfer">Transferencia bancaria</option>
                </select>
              </label>
              <div className="sale-modal-actions">
                <button type="button" className="secondary-button" disabled={saving} onClick={() => setShowForm(false)}>Cancelar</button>
                <button type="button" className="primary-button" disabled={saving || !selectedCustomer || cart.length === 0} onClick={() => void registerSale()}>{saving ? 'Confirmando...' : 'Registrar venta'}</button>
              </div>
            </div>
          </div>
        </FormModal>
      )}

      <section className="panel">
        <div className="panel-header"><div><span className="eyebrow">HISTORIAL</span><h2>Ventas registradas</h2><p>El vendedor ve solo sus ventas; administración y gerencia ven todas.</p></div></div>
        <div className="panel-toolbar">
          <input className="search-input" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por número de venta..." />
        </div>
        {sales.loading ? (
          <StateMessage type="loading" title="Cargando ventas" />
        ) : sales.error ? (
          <StateMessage type="error" title="No se pudo cargar" description={sales.error} actionLabel="Reintentar" onAction={sales.reload} />
        ) : (
          <div className="table-wrapper">
            <table>
              <thead><tr><th>Venta</th><th>Cliente</th><th>Vendedor</th><th>Fecha</th><th>Unidades</th><th>Total</th><th>Pago</th><th>Estado</th></tr></thead>
              <tbody>
                {sales.data.items.map((sale) => (
                  <tr key={sale.id}>
                    <td><strong>{sale.number}</strong></td>
                    <td>{sale.customer.name}</td>
                    <td>{sale.seller.name}</td>
                    <td>{formatDate(sale.created_at)}</td>
                    <td>{sale.items_count}</td>
                    <td>S/ {money(sale.total)}</td>
                    <td>{paymentLabels[sale.payment_method]}</td>
                    <td><span className="status-pill success">Confirmada</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {sales.data.items.length === 0 && <div className="empty-state">Todavía no hay ventas registradas.</div>}
          </div>
        )}
      </section>
    </div>
  )
}

export default Sales
