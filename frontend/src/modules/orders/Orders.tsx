import { useCallback, useEffect, useMemo, useState } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useProducts } from '../../hooks/useCatalog'
import { useCustomers } from '../../hooks/useCustomers'
import { changeOrderStatus, convertOrder, createOrder, listOrders, updateOrder } from '../../services/operations'
import type { OrderRecord, OrderStatus, PaymentMethod, ProductRecord } from '../../types/api'

interface Props { role: UserRole }
interface CartItem { product: ProductRecord; quantity: number }
const labels: Record<OrderStatus, string> = { draft: 'Borrador', pending: 'Pendiente', approved: 'Aprobado', cancelled: 'Cancelado', converted: 'Convertido' }
const money = (value: string | number) => Number(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

function Orders({ role }: Props) {
  const canManage = role !== 'manager'
  const [orders, setOrders] = useState<OrderRecord[]>([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<OrderRecord | null>(null)
  const [customerId, setCustomerId] = useState('')
  const [productId, setProductId] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [cart, setCart] = useState<CartItem[]>([])
  const [busy, setBusy] = useState(false)
  const [payment, setPayment] = useState<PaymentMethod>('cash')
  const customers = useCustomers({ page: 1, pageSize: 100, search: '', status: 'active' })
  const products = useProducts({ page: 1, pageSize: 100, search: '', categoryId: null, status: 'active' })
  const load = useCallback(() => {
    setLoading(true)
    listOrders(filter)
      .then((data) => setOrders(data.items))
      .catch((e: unknown) => setError(
        e instanceof Error ? e.message : 'No se pudieron cargar los pedidos.',
      ))
      .finally(() => setLoading(false))
  }, [filter])
  useEffect(() => {
    const timer = window.setTimeout(load, 0)
    return () => window.clearTimeout(timer)
  }, [load])
  const total = useMemo(() => cart.reduce((sum, item) => sum + Number(item.product.unit_price) * item.quantity, 0), [cart])

  const openCreate = () => { setEditing(null); setCustomerId(''); setCart([]); setError(''); setShowForm(true) }
  const openEdit = (order: OrderRecord) => {
    setEditing(order); setCustomerId(String(order.customer_id));
    setCart(order.items.map((item) => ({ product: products.data.items.find((p) => p.id === item.product_id) ?? { id: item.product_id, sku: item.sku, name: item.product_name, description: null, category_id: 0, category_name: item.category_name, unit_price: item.unit_price, stock: 0, active: true, created_at: '', updated_at: '' }, quantity: item.quantity })))
    setShowForm(true)
  }
  const addItem = () => {
    const product = products.data.items.find((item) => item.id === Number(productId)); const requested = Number(quantity)
    if (!product || requested < 1) return setError('Selecciona un producto y una cantidad válida.')
    const existing = cart.find((item) => item.product.id === product.id)
    setCart(existing ? cart.map((item) => item.product.id === product.id ? { ...item, quantity: item.quantity + requested } : item) : [...cart, { product, quantity: requested }])
    setProductId(''); setQuantity('1'); setError('')
  }
  const save = async () => {
    if (!customerId || !cart.length) return setError('Selecciona un cliente y agrega productos.')
    setBusy(true); setError('')
    const payload = { customer_id: Number(customerId), items: cart.map((item) => ({ product_id: item.product.id, quantity: item.quantity })) }
    try { const result = editing ? await updateOrder(editing.id, payload) : await createOrder(payload); setSuccess(`${result.number} guardado correctamente.`); setShowForm(false); load() }
    catch (e) { setError(e instanceof Error ? e.message : 'No se pudo guardar el pedido.') } finally { setBusy(false) }
  }
  const action = async (operation: () => Promise<unknown>, message: string) => { setBusy(true); setError(''); try { await operation(); setSuccess(message); load() } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo actualizar el pedido.') } finally { setBusy(false) } }

  return <div className="page">
    <PageHeader eyebrow="OPERACIÓN COMERCIAL" title="Pedidos" description="Prepara, aprueba y convierte pedidos en ventas con validación final de stock." action={canManage ? <button className="primary-button compact" onClick={openCreate}>+ Nuevo pedido</button> : undefined} />
    {success && <StateMessage type="success" title="Operación completada" description={success} />}
    {error && !showForm && <StateMessage type="error" title="No se pudo completar" description={error} />}
    <section className="panel"><div className="panel-header"><div><span className="eyebrow">SEGUIMIENTO</span><h2>Pedidos comerciales</h2><p>El inventario se descuenta únicamente al convertir un pedido aprobado.</p></div></div>
      <div className="panel-toolbar"><select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="">Todos los estados</option>{Object.entries(labels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
      {loading ? <StateMessage type="loading" title="Cargando pedidos" /> : <div className="table-wrapper"><table><thead><tr><th>Pedido</th><th>Cliente</th><th>Vendedor</th><th>Fecha</th><th>Productos</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>{orders.map((order) => <tr key={order.id}><td><strong>{order.number}</strong>{order.sale_id && <small>Venta V-{String(order.sale_id).padStart(6, '0')}</small>}</td><td>{order.customer_name}</td><td>{order.seller_name}</td><td>{new Date(order.created_at).toLocaleString('es-PE')}</td><td>{order.items.reduce((sum, item) => sum + item.quantity, 0)}</td><td>S/ {money(order.total)}</td><td><span className={`status-pill ${order.status === 'cancelled' ? 'danger' : order.status === 'converted' ? 'success' : ''}`}>{labels[order.status]}</span></td><td><div className="table-actions">{canManage && order.status === 'pending' && <><button className="text-button" onClick={() => openEdit(order)}>Editar</button><button className="text-button" disabled={busy} onClick={() => void action(() => changeOrderStatus(order.id, 'approved'), 'Pedido aprobado.')}>Aprobar</button></>}{canManage && ['pending', 'approved'].includes(order.status) && <button className="text-button danger" disabled={busy} onClick={() => void action(() => changeOrderStatus(order.id, 'cancelled'), 'Pedido cancelado.')}>Cancelar</button>}{canManage && order.status === 'approved' && <><select value={payment} onChange={(e) => setPayment(e.target.value as PaymentMethod)}><option value="cash">Efectivo</option><option value="card">Tarjeta</option><option value="bank_transfer">Transferencia</option></select><button className="primary-button compact" disabled={busy} onClick={() => void action(() => convertOrder(order.id, payment), 'Pedido convertido en venta.')}>Convertir</button></>}</div></td></tr>)}</tbody></table>{!orders.length && <div className="empty-state">No hay pedidos con este filtro.</div>}</div>}
    </section>
    {showForm && <FormModal eyebrow={editing ? 'EDITAR PEDIDO' : 'NUEVO PEDIDO'} title={editing ? editing.number : 'Crear pedido'} description="Los precios se toman del catálogo actual." onClose={() => setShowForm(false)} closeDisabled={busy} size="wide"><div className="sale-modal-content">{error && <StateMessage type="error" title="Revisa el pedido" description={error} />}<div className="sale-form"><label>Cliente<select value={customerId} onChange={(e) => setCustomerId(e.target.value)}><option value="">Seleccionar</option>{customers.data.items.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label>Producto<select value={productId} onChange={(e) => setProductId(e.target.value)}><option value="">Seleccionar</option>{products.data.items.map((item) => <option key={item.id} value={item.id}>{item.sku} · {item.name}</option>)}</select></label><label>Cantidad<input type="number" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} /></label><button type="button" className="primary-button" onClick={addItem}>Agregar</button></div><div className="cart-list">{cart.map((item) => <div className="cart-row" key={item.product.id}><div><strong>{item.product.name}</strong><span>{item.quantity} × S/ {money(item.product.unit_price)}</span></div><strong>S/ {money(Number(item.product.unit_price) * item.quantity)}</strong><button className="remove-button" onClick={() => setCart(cart.filter((row) => row.product.id !== item.product.id))}>Quitar</button></div>)}</div><div className="sale-summary"><div><span>Total estimado</span><strong>S/ {money(total)}</strong></div><div className="sale-modal-actions"><button className="secondary-button" onClick={() => setShowForm(false)}>Cancelar</button><button className="primary-button" disabled={busy} onClick={() => void save()}>{busy ? 'Guardando…' : 'Guardar pedido'}</button></div></div></div></FormModal>}
  </div>
}

export default Orders
