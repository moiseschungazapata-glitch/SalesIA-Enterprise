import { useCallback, useEffect, useMemo, useState } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { listSales } from '../../services/operations'
import { createPayment, listPayments, reversePayment } from '../../services/payments'
import type { PaymentMethod, PaymentRecord, PaymentStatus, SaleListItem } from '../../types/api'

const money = (value: string | number) => Number(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const methods: Record<PaymentMethod, string> = { cash: 'Efectivo', card: 'Tarjeta', bank_transfer: 'Transferencia' }
const statuses: Record<PaymentStatus, string> = { completed: 'Completado', cancelled: 'Anulado', refunded: 'Devuelto' }

export default function Payments({ role }: { role: UserRole }) {
  const [items, setItems] = useState<PaymentRecord[]>([])
  const [sales, setSales] = useState<SaleListItem[]>([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [saleId, setSaleId] = useState('')
  const [method, setMethod] = useState<PaymentMethod>('cash')
  const [amount, setAmount] = useState('')
  const [reference, setReference] = useState('')
  const canManage = role !== 'manager'

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [payments, saleData] = await Promise.all([
        listPayments(filter),
        listSales({ page: 1, pageSize: 100, number: '' }),
      ])
      setItems(payments.items)
      setSales(saleData.items.filter((sale) => Number(sale.balance_due) > 0))
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'No se pudieron cargar los pagos.') }
    finally { setLoading(false) }
  }, [filter])
  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0)
    return () => window.clearTimeout(timer)
  }, [load])
  const selectedSale = sales.find((sale) => sale.id === Number(saleId))
  const collected = useMemo(() => items.filter((item) => item.status === 'completed').reduce((sum, item) => sum + Number(item.amount), 0), [items])

  const save = async () => {
    if (!saleId || Number(amount) <= 0) return setError('Selecciona una venta e ingresa un abono válido.')
    try {
      await createPayment({ sale_id: Number(saleId), method, amount, reference: reference || null })
      setShowForm(false); setSuccess('Pago registrado correctamente.'); setSaleId(''); setAmount(''); setReference(''); await load()
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'No se pudo registrar el pago.') }
  }

  const reverse = async (item: PaymentRecord, action: 'cancel' | 'refund') => {
    const reason = window.prompt(action === 'refund' ? 'Motivo de la devolución:' : 'Motivo de la anulación:')
    if (!reason) return
    try { await reversePayment(item.id, action, reason); setSuccess(action === 'refund' ? 'Pago devuelto.' : 'Pago anulado.'); await load() }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'No se pudo revertir el pago.') }
  }

  return <div className="page">
    <PageHeader eyebrow="COBRANZAS" title="Pagos" description="Gestiona abonos, saldos pendientes, comprobantes y devoluciones." action={canManage ? <button className="primary-button compact" onClick={() => setShowForm(true)}>+ Registrar pago</button> : undefined} />
    {success && <StateMessage type="success" title={success} />}{error && <StateMessage type="error" title="No se pudo completar" description={error} />}
    <section className="kpi-grid"><article className="kpi-card"><span>Cobrado en la vista</span><strong className="kpi-value">S/ {money(collected)}</strong></article><article className="kpi-card"><span>Operaciones</span><strong className="kpi-value">{items.length}</strong></article></section>
    <section className="panel"><div className="panel-toolbar"><select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="">Todos los estados</option><option value="completed">Completados</option><option value="cancelled">Anulados</option><option value="refunded">Devueltos</option></select></div>
      {loading ? <StateMessage type="loading" title="Cargando pagos" /> : <div className="table-wrapper"><table><thead><tr><th>Venta</th><th>Cliente</th><th>Fecha</th><th>Método</th><th>Referencia</th><th>Importe</th><th>Saldo</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>{items.map((item) => <tr key={item.id}><td><strong>{item.sale_number}</strong></td><td>{item.customer_name}</td><td>{new Date(item.paid_at).toLocaleString('es-PE')}</td><td>{methods[item.method]}</td><td>{item.reference || '—'}</td><td>S/ {money(item.amount)}</td><td>S/ {money(item.balance_due)}</td><td><span className={`status-pill ${item.status !== 'completed' ? 'danger' : 'success'}`}>{statuses[item.status]}</span></td><td>{canManage && item.status === 'completed' && <div className="table-actions"><button className="text-button" onClick={() => void reverse(item, 'cancel')}>Anular</button><button className="text-button danger" onClick={() => void reverse(item, 'refund')}>Devolver</button></div>}</td></tr>)}</tbody></table>{!items.length && <div className="empty-state">No hay pagos con este filtro.</div>}</div>}
    </section>
    {showForm && <FormModal eyebrow="NUEVO ABONO" title="Registrar pago" description="El importe no puede superar el saldo de la venta." onClose={() => setShowForm(false)}><div className="form-grid"><label>Venta pendiente<select value={saleId} onChange={(e) => { setSaleId(e.target.value); const sale = sales.find((row) => row.id === Number(e.target.value)); setAmount(sale?.balance_due ?? '') }}><option value="">Seleccionar</option>{sales.map((sale) => <option key={sale.id} value={sale.id}>{sale.number} · {sale.customer.name} · saldo S/ {money(sale.balance_due)}</option>)}</select></label><label>Método<select value={method} onChange={(e) => setMethod(e.target.value as PaymentMethod)}>{Object.entries(methods).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label>Importe<input type="number" min="0.01" max={selectedSale?.balance_due} step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} /></label><label>Referencia o comprobante<input value={reference} maxLength={120} onChange={(e) => setReference(e.target.value)} placeholder="Opcional" /></label><div className="sale-modal-actions"><button className="secondary-button" onClick={() => setShowForm(false)}>Cancelar</button><button className="primary-button" onClick={() => void save()}>Registrar pago</button></div></div></FormModal>}
  </div>
}
