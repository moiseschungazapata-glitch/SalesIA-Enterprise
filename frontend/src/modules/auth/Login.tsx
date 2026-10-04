import { useState, type FormEvent } from 'react'
import ThemeToggle from '../../components/ThemeToggle'
import { useAuth } from '../../hooks/useAuth'

function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [passwordVisible, setPasswordVisible] = useState(false)

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
      <div className="login-theme-control">
        <ThemeToggle />
      </div>

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
            <span className="password-field">
              <input
                type={passwordVisible ? 'text' : 'password'}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Ingresa tu contraseña"
                autoComplete="current-password"
                minLength={12}
                maxLength={128}
                required
                disabled={submitting}
              />
              <button
                type="button"
                className="password-visibility-button"
                onClick={() => setPasswordVisible((visible) => !visible)}
                aria-label={passwordVisible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                title={passwordVisible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                aria-pressed={passwordVisible}
                disabled={submitting}
              >
                {passwordVisible ? (
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="m3 3 18 18M10.6 10.7a2 2 0 0 0 2.7 2.7M9.9 4.3A10.6 10.6 0 0 1 21 12a13 13 0 0 1-3.1 4.2M6.6 6.6A12.4 12.4 0 0 0 3 12s3.3 6 9 6a8.8 8.8 0 0 0 2.1-.3" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M3 12s3.3-6 9-6 9 6 9 6-3.3 6-9 6-9-6-9-6Z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                )}
              </button>
            </span>
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
