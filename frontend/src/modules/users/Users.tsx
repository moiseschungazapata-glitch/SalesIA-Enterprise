import { useMemo, useState, type FormEvent } from 'react'
import {
  roleLabels,
  type UserRole,
} from '../../app/navigation'
import FormModal from '../../components/FormModal'
import PageHeader from '../../components/PageHeader'
import StateMessage from '../../components/StateMessage'
import { useUsers } from '../../hooks/useUsers'
import { createUser, updateUser } from '../../services/users'

interface UsersProps {
  currentUserId: number
}

const pageSize = 10

const emptyForm = {
  name: '',
  email: '',
  role: 'seller' as UserRole,
  password: '',
  confirmPassword: '',
}

function Users({ currentUserId }: UsersProps) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('')
  const [statusFilter, setStatusFilter] = useState<
    'active' | 'inactive' | ''
  >('')
  const [showForm, setShowForm] = useState(false)
  const [formError, setFormError] = useState('')
  const [feedback, setFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [updatingId, setUpdatingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyForm)

  const filters = useMemo(
    () => ({
      page,
      pageSize,
      search,
      role: roleFilter,
      status: statusFilter,
    }),
    [page, search, roleFilter, statusFilter],
  )
  const { data, loading, error, reload } = useUsers(filters)
  const totalPages = Math.max(1, Math.ceil(data.total / pageSize))
  const visibleActive = data.items.filter((user) => user.active).length
  const visibleSellers = data.items.filter(
    (user) => user.role === 'seller',
  ).length
  const visibleManagers = data.items.filter(
    (user) => user.role === 'manager',
  ).length

  const resetFiltersPage = () => setPage(1)

  const refreshFromFirstPage = () => {
    if (page === 1) {
      reload()
    } else {
      setPage(1)
    }
  }

  const handleCreateUser = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    if (
      !form.name.trim() ||
      !form.email.trim() ||
      form.password.length < 12 ||
      form.password !== form.confirmPassword
    ) {
      setFormError(
        'Completa los campos y usa una contraseña coincidente de al menos 12 caracteres.',
      )
      return
    }

    setFormError('')
    setFeedback('')
    setSubmitting(true)

    try {
      await createUser({
        name: form.name.trim(),
        email: form.email.trim(),
        role: form.role,
        password: form.password,
      })
      setForm(emptyForm)
      setShowForm(false)
      setFeedback('Usuario creado correctamente en Supabase.')
      refreshFromFirstPage()
    } catch (requestError) {
      setFormError(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible crear el usuario.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  const toggleUser = async (userId: number, active: boolean) => {
    setUpdatingId(userId)
    setFeedback('')

    try {
      await updateUser(userId, { active: !active })
      setFeedback(
        active
          ? 'Usuario desactivado correctamente.'
          : 'Usuario activado correctamente.',
      )
      reload()
    } catch (requestError) {
      setFeedback(
        requestError instanceof Error
          ? requestError.message
          : 'No fue posible actualizar el usuario.',
      )
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="ADMINISTRACIÓN"
        title="Usuarios"
        description="Gestiona usuarios, roles y estados de acceso almacenados en Supabase."
        action={
          <button
            type="button"
            className="primary-button compact"
            onClick={() => {
              setShowForm(true)
              setFormError('')
            }}
          >
            + Nuevo usuario
          </button>
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
          <span>Vendedores visibles</span>
          <strong>{visibleSellers}</strong>
        </article>
        <article className="mini-stat">
          <span>Gerentes visibles</span>
          <strong>{visibleManagers}</strong>
        </article>
      </section>

      {feedback && (
        <div className="form-success" role="status" aria-live="polite">
          {feedback}
        </div>
      )}

      {showForm && (
        <FormModal
          eyebrow="NUEVO REGISTRO"
          title="Crear usuario"
          description="El usuario se guardará activo y con uno de los roles autorizados."
          onClose={() => setShowForm(false)}
          closeDisabled={submitting}
        >
          <form className="entity-form" onSubmit={handleCreateUser}>
            <label>
              Nombre completo
              <input
                value={form.name}
                onChange={(event) =>
                  setForm({ ...form, name: event.target.value })
                }
                placeholder="Nombre y apellidos"
                minLength={2}
                maxLength={160}
                required
                disabled={submitting}
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
                required
                disabled={submitting}
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
                disabled={submitting}
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
                minLength={12}
                maxLength={128}
                autoComplete="new-password"
                required
                disabled={submitting}
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
                minLength={12}
                maxLength={128}
                autoComplete="new-password"
                required
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
                {submitting ? 'Creando…' : 'Crear usuario'}
              </button>
            </div>
          </form>
        </FormModal>
      )}

      <section className="panel">
        <div className="panel-toolbar users-toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              resetFiltersPage()
            }}
            placeholder="Buscar por nombre o correo..."
          />
          <select
            className="select-input"
            value={roleFilter}
            onChange={(event) => {
              setRoleFilter(event.target.value as UserRole | '')
              resetFiltersPage()
            }}
          >
            <option value="">Todos los roles</option>
            <option value="administrator">Administrador</option>
            <option value="seller">Vendedor</option>
            <option value="manager">Gerente</option>
          </select>
          <select
            className="select-input"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(
                event.target.value as 'active' | 'inactive' | '',
              )
              resetFiltersPage()
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
            title="Cargando usuarios"
            description="Consultando los usuarios registrados en Supabase."
          />
        ) : error ? (
          <StateMessage
            type="error"
            title="No se pudieron cargar los usuarios"
            description={error}
            actionLabel="Reintentar"
            onAction={reload}
          />
        ) : data.items.length === 0 ? (
          <StateMessage
            type="empty"
            title="No se encontraron usuarios"
            description="Cambia los filtros o crea un nuevo usuario."
          />
        ) : (
          <>
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
                  {data.items.map((user) => {
                    const isCurrentUser = user.id === currentUserId
                    return (
                      <tr key={user.id}>
                        <td>
                          <strong>{user.name}</strong>
                          {isCurrentUser && (
                            <span className="current-user-label">Tu sesión</span>
                          )}
                        </td>
                        <td>{user.email}</td>
                        <td>{roleLabels[user.role]}</td>
                        <td>
                          <span
                            className={`status-pill ${
                              user.active ? 'success' : 'neutral'
                            }`}
                          >
                            {user.active ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                        <td>
                          <button
                            type="button"
                            className="secondary-button compact"
                            onClick={() =>
                              void toggleUser(user.id, user.active)
                            }
                            disabled={
                              isCurrentUser || updatingId === user.id
                            }
                            title={
                              isCurrentUser
                                ? 'No puedes desactivar tu sesión actual'
                                : undefined
                            }
                          >
                            {updatingId === user.id
                              ? 'Guardando…'
                              : user.active
                                ? 'Desactivar'
                                : 'Activar'}
                          </button>
                        </td>
                      </tr>
                    )
                  })}
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
              <span>
                Página {page} de {totalPages}
              </span>
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

export default Users
