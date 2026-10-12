import { useMemo, useState, type FormEvent, type ReactNode } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useCustomers } from '../../hooks/useCustomers'
import {
  createCustomer,
  getCustomerHistory,
  updateCustomer,
} from '../../services/customers'
import type {
  CustomerHistoryResponse,
  CustomerRecord,
  CustomerType,
  DocumentType,
} from '../../types/api'

interface CustomersProps {
  role: UserRole
}

const pageSize = 10

const money = (value: string) => Number(value).toLocaleString('es-PE', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const dateTime = (value: string | null) => value
  ? new Date(value).toLocaleString('es-PE')
  : 'Sin compras'

const paymentLabels = {
  pending: 'Pendiente',
  partial: 'Parcial',
  paid: 'Pagada',
  refunded: 'Devuelta',
}

const methodLabels = {
  cash: 'Efectivo',
  card: 'Tarjeta',
  bank_transfer: 'Transferencia',
}

function HistoryTable({
  title,
  empty,
  hasItems,
  children,
}: {
  title: string
  empty: string
  hasItems: boolean
  children: ReactNode
}) {
  return (
    <section className="customer-history-section">
      <h3>{title}</h3>
      {hasItems ? (
        <div className="table-wrapper"><table>{children}</table></div>
      ) : (
        <p className="customer-history-empty">{empty}</p>
      )}
    </section>
  )
}

const emptyForm = {
  customerType: 'person' as CustomerType,
  documentType: 'DNI' as DocumentType,
  documentNumber: '',
  name: '',
  email: '',
  phone: '',
  address: '',
}

function Customers({ role }: CustomersProps) {
  const canManage = role === 'administrator'
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<
    'active' | 'inactive' | ''
  >('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [history, setHistory] = useState<CustomerHistoryResponse | null>(null)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')
  const [editingCustomer, setEditingCustomer] = useState(false)
  const [editForm, setEditForm] = useState({ name: '', email: '', phone: '', address: '' })
  const [formError, setFormError] = useState('')
  const [feedback, setFeedback] = useState('')
  const [feedbackIsError, setFeedbackIsError] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [updatingId, setUpdatingId] = useState<number | null>(null)

  const filters = useMemo(
    () => ({ page, pageSize, search, status: statusFilter }),
    [page, search, statusFilter],
  )
  const { data, loading, error, reload } = useCustomers(filters)
  const totalPages = Math.max(1, Math.ceil(data.total / pageSize))
  const visibleActive = data.items.filter((customer) => customer.active).length
  const visiblePeople = data.items.filter(
    (customer) => customer.customer_type === 'person',
  ).length
  const visibleCompanies = data.items.filter(
    (customer) => customer.customer_type === 'company',
  ).length

  const refreshFromFirstPage = () => {
    if (page === 1) reload()
    else setPage(1)
  }

  const showFeedback = (message: string, isError = false) => {
    setFeedback(message)
    setFeedbackIsError(isError)
  }

  const handleCustomerType = (customerType: CustomerType) => {
    setForm({
      ...form,
      customerType,
      documentType: customerType === 'person' ? 'DNI' : 'RUC',
      documentNumber: '',
    })
  }

  const handleAddCustomer = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const expectedLength = form.documentType === 'DNI' ? 8 : 11
    if (
      !form.name.trim() ||
      !/^\d+$/.test(form.documentNumber) ||
      form.documentNumber.length !== expectedLength
    ) {
      setFormError(
        `Completa el nombre e ingresa un ${form.documentType} de ${expectedLength} dígitos.`,
      )
      return
    }

    setFormError('')
    setFeedback('')
    setSubmitting(true)
    try {
      await createCustomer({
        customer_type: form.customerType,
        document_type: form.documentType,
        document_number: form.documentNumber,
        name: form.name.trim(),
        email: form.email.trim() || null,
        phone: form.phone.trim() || null,
        address: form.address.trim() || null,
      })
      setForm(emptyForm)
      setShowForm(false)
      showFeedback('Cliente creado correctamente en Supabase.')
      refreshFromFirstPage()
    } catch (requestError) {
      setFormError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible crear el cliente.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  const toggleCustomer = async (customerId: number, active: boolean) => {
    setUpdatingId(customerId)
    setFeedback('')
    try {
      await updateCustomer(customerId, { active: !active })
      showFeedback(
        active
          ? 'Cliente desactivado correctamente.'
          : 'Cliente activado correctamente.',
      )
      reload()
    } catch (requestError) {
      showFeedback(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible actualizar el cliente.',
        true,
      )
    } finally {
      setUpdatingId(null)
    }
  }

  const openHistory = async (customer: CustomerRecord) => {
    setHistory(null)
    setHistoryError('')
    setHistoryLoading(true)
    setEditingCustomer(false)
    setEditForm({
      name: customer.name,
      email: customer.email || '',
      phone: customer.phone || '',
      address: customer.address || '',
    })
    try {
      setHistory(await getCustomerHistory(customer.id))
    } catch (requestError) {
      setHistoryError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible consultar el historial.',
      )
    } finally {
      setHistoryLoading(false)
    }
  }

  const saveCustomerChanges = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!history || !editForm.name.trim()) return
    setSubmitting(true)
    setHistoryError('')
    try {
      await updateCustomer(history.customer.id, {
        name: editForm.name.trim(),
        email: editForm.email.trim() || null,
        phone: editForm.phone.trim() || null,
        address: editForm.address.trim() || null,
      })
      setHistory(await getCustomerHistory(history.customer.id))
      setEditingCustomer(false)
      showFeedback('Datos del cliente actualizados correctamente.')
      reload()
    } catch (requestError) {
      setHistoryError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible actualizar el cliente.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="GESTIÓN COMERCIAL"
        title="Clientes"
        description={
          canManage
            ? 'Consulta y administra la cartera real de clientes.'
            : 'Consulta la cartera de clientes según tu perfil.'
        }
        action={
          canManage ? (
            <button
              type="button"
              className="primary-button compact"
              onClick={() => {
                setShowForm(true)
                setFormError('')
              }}
            >
              + Nuevo cliente
            </button>
          ) : undefined
        }
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Resultados</span>
          <strong>{data.total}</strong>
        </article>
        <article className="mini-stat">
          <span>Activos visibles</span>
          <strong>{visibleActive}</strong>
        </article>
        <article className="mini-stat">
          <span>Personas visibles</span>
          <strong>{visiblePeople}</strong>
        </article>
        <article className="mini-stat">
          <span>Empresas visibles</span>
          <strong>{visibleCompanies}</strong>
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

      {canManage && showForm && (
        <FormModal
          eyebrow="NUEVO REGISTRO"
          title="Agregar cliente"
          description="Registra una persona con DNI o una empresa con RUC."
          onClose={() => setShowForm(false)}
          closeDisabled={submitting}
        >
          <form className="entity-form" onSubmit={handleAddCustomer}>
            <label>
              Tipo de cliente
              <select
                value={form.customerType}
                onChange={(event) =>
                  handleCustomerType(event.target.value as CustomerType)
                }
                disabled={submitting}
              >
                <option value="person">Persona</option>
                <option value="company">Empresa</option>
              </select>
            </label>
            <label>
              {form.documentType}
              <input
                inputMode="numeric"
                value={form.documentNumber}
                onChange={(event) =>
                  setForm({
                    ...form,
                    documentNumber: event.target.value.replace(/\D/g, ''),
                  })
                }
                maxLength={form.documentType === 'DNI' ? 8 : 11}
                placeholder={form.documentType === 'DNI' ? '12345678' : '20123456789'}
                required
                disabled={submitting}
              />
            </label>
            <label>
              Nombre o razón social
              <input
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                minLength={2}
                maxLength={200}
                required
                disabled={submitting}
              />
            </label>
            <label>
              Correo
              <input
                type="email"
                value={form.email}
                onChange={(event) => setForm({ ...form, email: event.target.value })}
                placeholder="correo@empresa.com"
                disabled={submitting}
              />
            </label>
            <label>
              Teléfono
              <input
                value={form.phone}
                onChange={(event) => setForm({ ...form, phone: event.target.value })}
                maxLength={30}
                placeholder="987 654 321"
                disabled={submitting}
              />
            </label>
            <label>
              Dirección
              <input
                value={form.address}
                onChange={(event) => setForm({ ...form, address: event.target.value })}
                maxLength={500}
                placeholder="Lima"
                disabled={submitting}
              />
            </label>

            {formError && (
              <div className="form-error" role="alert">
                {formError}
              </div>
            )}

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowForm(false)}
                disabled={submitting}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="primary-button"
                disabled={submitting}
              >
                {submitting ? 'Guardando…' : 'Guardar cliente'}
              </button>
            </div>
          </form>
        </FormModal>
      )}

      {(historyLoading || history || historyError) && (
        <FormModal
          eyebrow="EXPEDIENTE COMERCIAL"
          title={history?.customer.name || 'Historial del cliente'}
          description="Información de contacto y actividad comercial consolidada."
          size="wide"
          onClose={() => {
            setHistory(null)
            setHistoryError('')
            setHistoryLoading(false)
          }}
          closeDisabled={submitting}
        >
          {historyLoading ? (
            <StateMessage type="loading" title="Cargando historial" />
          ) : historyError && !history ? (
            <StateMessage type="error" title="No se pudo abrir el cliente" description={historyError} />
          ) : history ? (
            <div className="customer-history">
              <section className="customer-profile-strip">
                <div><span>Documento</span><strong>{history.customer.document_type} {history.customer.document_number}</strong></div>
                <div><span>Correo</span><strong>{history.customer.email || 'Sin correo'}</strong></div>
                <div><span>Teléfono</span><strong>{history.customer.phone || 'Sin teléfono'}</strong></div>
                <div><span>Estado</span><strong>{history.customer.active ? 'Activo' : 'Inactivo'}</strong></div>
              </section>

              {canManage && (
                <div className="customer-history-actions">
                  <button type="button" className="secondary-button compact" onClick={() => setEditingCustomer((value) => !value)}>
                    {editingCustomer ? 'Cancelar edición' : 'Editar cliente'}
                  </button>
                </div>
              )}

              {editingCustomer && (
                <form className="entity-form customer-edit-form" onSubmit={saveCustomerChanges}>
                  <label>Nombre o razón social<input value={editForm.name} minLength={2} maxLength={200} required onChange={(event) => setEditForm({ ...editForm, name: event.target.value })} /></label>
                  <label>Correo<input type="email" value={editForm.email} onChange={(event) => setEditForm({ ...editForm, email: event.target.value })} /></label>
                  <label>Teléfono<input value={editForm.phone} maxLength={30} onChange={(event) => setEditForm({ ...editForm, phone: event.target.value })} /></label>
                  <label>Dirección<input value={editForm.address} maxLength={500} onChange={(event) => setEditForm({ ...editForm, address: event.target.value })} /></label>
                  <div className="form-actions"><button type="submit" className="primary-button" disabled={submitting}>{submitting ? 'Guardando…' : 'Guardar cambios'}</button></div>
                </form>
              )}

              {historyError && <div className="form-error" role="alert">{historyError}</div>}

              <section className="customer-summary-grid">
                <article><span>Total comprado</span><strong>S/ {money(history.summary.total_purchased)}</strong></article>
                <article><span>Total pagado</span><strong>S/ {money(history.summary.total_paid)}</strong></article>
                <article><span>Saldo pendiente</span><strong>S/ {money(history.summary.balance_due)}</strong></article>
                <article><span>Compras</span><strong>{history.summary.sales_count}</strong></article>
                <article><span>Ticket promedio</span><strong>S/ {money(history.summary.average_ticket)}</strong></article>
                <article><span>Última compra</span><strong>{dateTime(history.summary.last_purchase_at)}</strong></article>
              </section>

              <HistoryTable title="Ventas" empty="Este cliente todavía no tiene ventas." hasItems={history.sales.length > 0}>
                <thead><tr><th>Venta</th><th>Fecha</th><th>Vendedor</th><th>Unidades</th><th>Pago</th><th>Total</th><th>Saldo</th></tr></thead>
                <tbody>{history.sales.map((sale) => <tr key={sale.id}><td><strong>{sale.number}</strong></td><td>{dateTime(sale.created_at)}</td><td>{sale.seller_name}</td><td>{sale.units}</td><td><span className="status-pill neutral">{paymentLabels[sale.payment_status]}</span></td><td>S/ {money(sale.total)}</td><td>S/ {money(sale.balance_due)}</td></tr>)}</tbody>
              </HistoryTable>

              <HistoryTable title="Pedidos" empty="Este cliente todavía no tiene pedidos." hasItems={history.orders.length > 0}>
                <thead><tr><th>Pedido</th><th>Fecha</th><th>Vendedor</th><th>Estado</th><th>Venta</th><th>Total</th></tr></thead>
                <tbody>{history.orders.map((order) => <tr key={order.id}><td><strong>{order.number}</strong></td><td>{dateTime(order.created_at)}</td><td>{order.seller_name}</td><td>{order.status}</td><td>{order.sale_id ? `V-${String(order.sale_id).padStart(6, '0')}` : '—'}</td><td>S/ {money(order.total)}</td></tr>)}</tbody>
              </HistoryTable>

              <HistoryTable title="Pagos y devoluciones" empty="No existen pagos registrados." hasItems={history.payments.length > 0}>
                <thead><tr><th>Venta</th><th>Fecha</th><th>Método</th><th>Referencia</th><th>Estado</th><th>Importe</th></tr></thead>
                <tbody>{history.payments.map((payment) => <tr key={payment.id}><td><strong>{payment.sale_number}</strong></td><td>{dateTime(payment.paid_at)}</td><td>{methodLabels[payment.method]}</td><td>{payment.reference || '—'}</td><td>{payment.status}</td><td>S/ {money(payment.amount)}</td></tr>)}</tbody>
              </HistoryTable>

              <HistoryTable title="Productos comprados" empty="No existen productos comprados." hasItems={history.products.length > 0}>
                <thead><tr><th>Producto</th><th>SKU</th><th>Unidades</th><th>Compras</th><th>Última compra</th><th>Total</th></tr></thead>
                <tbody>{history.products.map((product) => <tr key={`${product.product_id}-${product.sku}`}><td><strong>{product.name}</strong></td><td>{product.sku}</td><td>{product.units}</td><td>{product.purchase_count}</td><td>{dateTime(product.last_purchase_at)}</td><td>S/ {money(product.total)}</td></tr>)}</tbody>
              </HistoryTable>
            </div>
          ) : null}
        </FormModal>
      )}

      <section className="panel">
        <div className="panel-toolbar customers-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
            placeholder="Buscar por nombre, documento, correo o teléfono..."
          />
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
          Página {data.page} de {totalPages} · {data.total} resultado(s)
        </div>

        {loading ? (
          <StateMessage
            type="loading"
            title="Cargando clientes"
            description="Consultando la cartera registrada en Supabase."
          />
        ) : error ? (
          <StateMessage
            type="error"
            title="No se pudieron cargar los clientes"
            description={error}
            actionLabel="Reintentar"
            onAction={reload}
          />
        ) : data.items.length === 0 ? (
          <StateMessage
            type="empty"
            title="No se encontraron clientes"
            description="Cambia los filtros o registra el primer cliente."
          />
        ) : (
          <>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Documento</th>
                    <th>Contacto</th>
                    <th>Dirección</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((customer) => (
                    <tr key={customer.id}>
                      <td>
                        <strong>{customer.name}</strong>
                        <span className="table-subtitle">
                          {customer.customer_type === 'person' ? 'Persona' : 'Empresa'}
                        </span>
                      </td>
                      <td>
                        {customer.document_type} {customer.document_number}
                      </td>
                      <td>
                        {customer.email || 'Sin correo'}
                        <span className="table-subtitle">
                          {customer.phone || 'Sin teléfono'}
                        </span>
                      </td>
                      <td>{customer.address || 'Sin dirección'}</td>
                      <td>
                        <span
                          className={`status-pill ${
                            customer.active ? 'success' : 'neutral'
                          }`}
                        >
                          {customer.active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        <div className="table-actions">
                          <button type="button" className="text-button" onClick={() => void openHistory(customer)}>Ver historial</button>
                          {canManage && (
                          <button
                            type="button"
                            className="secondary-button compact"
                            onClick={() =>
                              void toggleCustomer(customer.id, customer.active)
                            }
                            disabled={updatingId === customer.id}
                          >
                            {updatingId === customer.id
                              ? 'Guardando…'
                              : customer.active
                                ? 'Desactivar'
                                : 'Activar'}
                          </button>
                          )}
                        </div>
                      </td>
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

export default Customers
