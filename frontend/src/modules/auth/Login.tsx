import { useState, type FormEvent } from 'react'
import { useAuth } from '../../hooks/useAuth'

function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!email.trim() || password.length < 12) {
      setError(
        'Ingresa un correo válido y una contraseña de al menos 12 caracteres.',
      )
      return
    }

    setError('')
    setSubmitting(true)

    try {
      await login(email.trim(), password)
    } catch (loginError) {
      setError(
        loginError instanceof Error
          ? loginError.message
          : 'No fue posible iniciar sesión.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="login-brand">
          <div className="brand-mark large">S</div>
          <div>
            <strong>SalesIA</strong>
            <span>Enterprise</span>
          </div>
        </div>

        <div className="login-copy">
          <span className="eyebrow">PLATAFORMA EMPRESARIAL</span>
          <h1>Bienvenido de nuevo.</h1>
          <p>
            Ingresa con el usuario registrado en SalesIA Enterprise.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Correo electrónico
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="usuario@empresa.com"
              autoComplete="email"
              required
              disabled={submitting}
            />
          </label>

          <label>
            Contraseña
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Ingresa tu contraseña"
              autoComplete="current-password"
              minLength={12}
              maxLength={128}
              required
              disabled={submitting}
            />
          </label>

          {error && (
            <div className="form-error" role="alert" aria-live="polite">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="primary-button"
            disabled={submitting}
          >
            {submitting ? 'Verificando acceso…' : 'Ingresar al sistema'}
          </button>
        </form>

        <div className="login-footer">
          SalesIA Enterprise · Acceso protegido mediante JWT
        </div>
      </section>
    </main>
  )
}

export default Login
