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

      <section className="login-panel auth-login-panel">
        <aside className="login-showcase" aria-label="Beneficios de SalesIA Enterprise">
          <div className="login-brand login-showcase-brand">
            <div className="brand-mark large">S</div>
            <div><strong>SalesIA</strong><span>Enterprise</span></div>
          </div>

          <div className="login-showcase-copy">
            <h2>Convierte datos en mejores decisiones.</h2>
            <p>Todo el control comercial que necesitas, en un solo lugar.</p>
          </div>

          <div className="login-benefits">
            <div><span aria-hidden="true">▥</span><strong>Gestión comercial centralizada</strong></div>
            <div><span aria-hidden="true">◇</span><strong>Información protegida</strong></div>
            <div><span aria-hidden="true">↗</span><strong>Análisis para crecer</strong></div>
          </div>

          <div className="login-showcase-chart" aria-hidden="true">
            <i /><i /><i /><i /><i /><i /><i /><i />
            <svg viewBox="0 0 500 120" preserveAspectRatio="none">
              <path d="M0 95 C75 35 120 110 190 70 S300 100 365 42 S445 48 500 8" />
            </svg>
          </div>
        </aside>

        <div className="login-form-side">
          <div className="login-mobile-brand login-brand">
            <div className="brand-mark large">S</div>
            <div><strong>SalesIA</strong><span>Enterprise</span></div>
          </div>

          <div className="login-copy">
            <span className="eyebrow">ACCESO SEGURO</span>
            <h1>Bienvenido de nuevo.</h1>
            <p>Ingresa con tu cuenta de SalesIA Enterprise.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              Correo electrónico
              <span className="login-input-field">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6.5h18v12H3zM3.5 7l8.5 6 8.5-6" /></svg>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="usuario@empresa.com"
                  autoComplete="email"
                  required
                  disabled={submitting}
                />
              </span>
            </label>

            <label>
              Contraseña
              <span className="password-field login-input-field">
                <svg className="login-input-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
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

            {error && <div className="form-error" role="alert" aria-live="polite">{error}</div>}

            <button type="submit" className="primary-button login-submit" disabled={submitting}>
              {submitting ? 'Verificando acceso…' : 'Ingresar al sistema'}
            </button>
          </form>

          <div className="login-security-note">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V6z" /><path d="M9 12l2 2 4-4" /></svg>
            <div><strong>Acceso protegido</strong><span>La ubicación ayuda a proteger y registrar el acceso.</span></div>
          </div>

          <div className="login-footer">
            SalesIA Enterprise · Acceso protegido mediante JWT
          </div>
        </div>
      </section>
    </main>
  )
}

export default Login
