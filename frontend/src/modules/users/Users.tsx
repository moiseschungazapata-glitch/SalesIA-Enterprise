import { useMemo, useState } from 'react'
import {
  roleLabels,
  type UserRole,
} from '../../app/navigation'
import PageHeader from '../../components/PageHeader'

interface UserRecord {
  id: number
  name: string
  email: string
  role: UserRole
  status: 'Activo' | 'Inactivo'
}

const initialUsers: UserRecord[] = [
  {
    id: 1,
    name: 'Carlos Rivera',
    email: 'carlos.rivera@salesia.pe',
    role: 'administrator',
    status: 'Activo',
  },
  {
    id: 2,
    name: 'María Torres',
    email: 'maria.torres@salesia.pe',
    role: 'seller',
    status: 'Activo',
  },
  {
    id: 3,
    name: 'Lucía Vega',
    email: 'lucia.vega@salesia.pe',
    role: 'manager',
    status: 'Activo',
  },
  {
    id: 4,
    name: 'Diego Salas',
    email: 'diego.salas@salesia.pe',
    role: 'seller',
    status: 'Inactivo',
  },
]

function Users() {
  const [users, setUsers] =
    useState<UserRecord[]>(initialUsers)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('Todos')
  const [statusFilter, setStatusFilter] = useState('Todos')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '',
    email: '',
    role: 'seller' as UserRole,
    password: '',
    confirmPassword: '',
  })

  const filteredUsers = useMemo(() => {
    const normalizedSearch = search.toLowerCase()

    return users.filter((user) => {
      const matchesSearch =
        user.name.toLowerCase().includes(normalizedSearch) ||
        user.email.toLowerCase().includes(normalizedSearch)
      const matchesRole =
        roleFilter === 'Todos' || user.role === roleFilter
      const matchesStatus =
        statusFilter === 'Todos' ||
        user.status === statusFilter

      return matchesSearch && matchesRole && matchesStatus
    })
  }, [users, search, roleFilter, statusFilter])

  const handleCreateUser = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    if (
      !form.name.trim() ||
      !form.email.trim() ||
      form.password.length < 12 ||
      form.password !== form.confirmPassword
    ) {
      setError(
        'Completa los campos y usa una contraseña coincidente de al menos 12 caracteres.',
      )
      return
    }

    if (
      users.some(
        (user) =>
          user.email.toLowerCase() === form.email.toLowerCase(),
      )
    ) {
      setError('Ya existe un usuario con ese correo electrónico.')
      return
    }

    setUsers((current) => [
      {
        id: Date.now(),
        name: form.name.trim(),
        email: form.email.trim(),
        role: form.role,
        status: 'Activo',
      },
      ...current,
    ])
    setForm({
      name: '',
      email: '',
      role: 'seller',
      password: '',
      confirmPassword: '',
    })
    setError('')
    setShowForm(false)
  }

  const toggleUser = (id: number) => {
    setUsers((current) =>
      current.map((user) =>
        user.id === id
          ? {
              ...user,
              status:
                user.status === 'Activo'
                  ? 'Inactivo'
                  : 'Activo',
            }
          : user,
      ),
    )
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="ADMINISTRACIÓN"
        title="Usuarios"
        description="Gestiona usuarios, roles y estados de acceso."
        action={
          <button
            type="button"
            className="primary-button compact"
            onClick={() => setShowForm((value) => !value)}
          >
            {showForm ? 'Cerrar' : '+ Nuevo usuario'}
          </button>
        }
      />

      <section className="kpi-grid compact-grid">
        <article className="mini-stat">
          <span>Total usuarios</span>
          <strong>{users.length}</strong>
        </article>
        <article className="mini-stat">
          <span>Activos</span>
          <strong>
            {users.filter((user) => user.status === 'Activo').length}
          </strong>
        </article>
        <article className="mini-stat">
          <span>Vendedores</span>
          <strong>
            {users.filter((user) => user.role === 'seller').length}
          </strong>
        </article>
        <article className="mini-stat">
          <span>Gerentes</span>
          <strong>
            {users.filter((user) => user.role === 'manager').length}
          </strong>
        </article>
      </section>

      {showForm && (
        <section className="panel form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">NUEVO REGISTRO</span>
              <h2>Crear usuario</h2>
              <p>
                El usuario se crea activo y recibe uno de los tres roles aprobados.
              </p>
            </div>
          </div>

          <form
            className="entity-form"
            onSubmit={handleCreateUser}
          >
            <label>
              Nombre completo
              <input
                value={form.name}
                onChange={(event) =>
                  setForm({ ...form, name: event.target.value })
                }
                placeholder="Nombre y apellidos"
              />
            </label>
            <label>
              Correo electrónico
              <input
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm({ ...form, email: event.target.value })
                }
                placeholder="usuario@empresa.com"
              />
            </label>
            <label>
              Rol
              <select
                value={form.role}
                onChange={(event) =>
                  setForm({
                    ...form,
                    role: event.target.value as UserRole,
                  })
                }
              >
                <option value="administrator">Administrador</option>
                <option value="seller">Vendedor</option>
                <option value="manager">Gerente</option>
              </select>
            </label>
            <label>
              Contraseña inicial
              <input
                type="password"
                value={form.password}
                onChange={(event) =>
                  setForm({ ...form, password: event.target.value })
                }
                placeholder="Mínimo 12 caracteres"
              />
            </label>
            <label>
              Confirmar contraseña
              <input
                type="password"
                value={form.confirmPassword}
                onChange={(event) =>
                  setForm({
                    ...form,
                    confirmPassword: event.target.value,
                  })
                }
                placeholder="Repite la contraseña"
              />
            </label>

            {error && <div className="form-error">{error}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowForm(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="primary-button">
                Crear usuario
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-toolbar users-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar por nombre o correo..."
          />
          <select
            className="select-input"
            value={roleFilter}
            onChange={(event) => setRoleFilter(event.target.value)}
          >
            <option>Todos</option>
            <option value="administrator">Administrador</option>
            <option value="seller">Vendedor</option>
            <option value="manager">Gerente</option>
          </select>
          <select
            className="select-input"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option>Todos</option>
            <option>Activo</option>
            <option>Inactivo</option>
          </select>
        </div>

        <div className="results-info">
          Mostrando {filteredUsers.length} de {users.length} usuarios
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td><strong>{user.name}</strong></td>
                  <td>{user.email}</td>
                  <td>{roleLabels[user.role]}</td>
                  <td>
                    <span
                      className={`status-pill ${
                        user.status === 'Activo'
                          ? 'success'
                          : 'neutral'
                      }`}
                    >
                      {user.status}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="secondary-button compact"
                      onClick={() => toggleUser(user.id)}
                    >
                      {user.status === 'Activo'
                        ? 'Desactivar'
                        : 'Activar'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredUsers.length === 0 && (
            <div className="empty-state">
              No se encontraron usuarios con esos filtros.
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default Users
