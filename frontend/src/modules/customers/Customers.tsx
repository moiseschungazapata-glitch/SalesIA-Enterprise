import { useMemo, useState, type FormEvent } from 'react'
import type { UserRole } from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useCustomers } from '../../hooks/useCustomers'
import {
  createCustomer,
  updateCustomer,
} from '../../services/customers'
import type {
  CustomerType,
  DocumentType,
} from '../../types/api'

interface CustomersProps {
  role: UserRole
}

const pageSize = 10

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
                    {canManage && <th>Acción</th>}
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
                      {canManage && (
                        <td>
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

export default Customers
