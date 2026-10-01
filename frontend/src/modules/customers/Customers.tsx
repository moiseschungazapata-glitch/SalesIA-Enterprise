import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader'
import { customers as initialCustomers } from '../../services/mockData'
import type { Customer } from '../../types'

function Customers() {
  const [customerList, setCustomerList] =
    useState<Customer[]>(initialCustomers)

  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('Todos')
  const [showForm, setShowForm] = useState(false)

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    city: '',
  })

  const filteredCustomers = useMemo(() => {
    return customerList.filter((customer) => {
      const matchesSearch =
        customer.name
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        customer.email
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        customer.city
          .toLowerCase()
          .includes(search.toLowerCase())

      const matchesStatus =
        statusFilter === 'Todos' ||
        customer.status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [customerList, search, statusFilter])

  const activeCustomers = customerList.filter(
    (customer) => customer.status === 'Activo',
  ).length

  const handleAddCustomer = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    if (
      !form.name.trim() ||
      !form.email.trim() ||
      !form.phone.trim() ||
      !form.city.trim()
    ) {
      return
    }

    const newCustomer: Customer = {
      id: Date.now(),
      name: form.name,
      email: form.email,
      phone: form.phone,
      city: form.city,
      purchases: 0,
      status: 'Activo',
    }

    setCustomerList((current) => [
      newCustomer,
      ...current,
    ])

    setForm({
      name: '',
      email: '',
      phone: '',
      city: '',
    })

    setShowForm(false)
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="GESTIÓN COMERCIAL"
        title="Clientes"
        description="Consulta y administra la cartera de clientes."
        action={
          <button
            type="button"
            className="primary-button compact"
            onClick={() => setShowForm((value) => !value)}
          >
            {showForm ? 'Cerrar' : '+ Nuevo cliente'}
          </button>
        }
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Total clientes</span>
          <strong>{customerList.length}</strong>
        </article>

        <article className="mini-stat">
          <span>Clientes activos</span>
          <strong>{activeCustomers}</strong>
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

      {showForm && (
        <section className="panel form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                NUEVO REGISTRO
              </span>
              <h2>Agregar cliente</h2>
              <p>
                Completa los datos básicos del cliente.
              </p>
            </div>
          </div>

          <form
            className="entity-form"
            onSubmit={handleAddCustomer}
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
                placeholder="Nombre del cliente"
              />
            </label>

            <label>
              Correo
              <input
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm({
                    ...form,
                    email: event.target.value,
                  })
                }
                placeholder="correo@empresa.com"
              />
            </label>

            <label>
              Teléfono
              <input
                value={form.phone}
                onChange={(event) =>
                  setForm({
                    ...form,
                    phone: event.target.value,
                  })
                }
                placeholder="987 654 321"
              />
            </label>

            <label>
              Ciudad
              <input
                value={form.city}
                onChange={(event) =>
                  setForm({
                    ...form,
                    city: event.target.value,
                  })
                }
                placeholder="Lima"
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
                Guardar cliente
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
            placeholder="Buscar por nombre, correo o ciudad..."
          />

          <select
            className="select-input"
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value)
            }
          >
            <option>Todos</option>
            <option>Activo</option>
            <option>Inactivo</option>
          </select>
        </div>

        <div className="results-info">
          Mostrando {filteredCustomers.length} de{' '}
          {customerList.length} clientes
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
              {filteredCustomers.map((customer) => (
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

          {filteredCustomers.length === 0 && (
            <div className="empty-state">
              No se encontraron clientes.
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default Customers
