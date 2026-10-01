import { useState, type FormEvent } from 'react'

interface LoginProps {
  onLogin: () => void
}

function Login({ onLogin }: LoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!email.trim() || !password.trim()) {
      setError('Completa el correo y la contraseña.')
      return
    }

    setError('')
    onLogin()
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
            Gestiona ventas, inventario y analítica desde
            un solo lugar.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Correo electrónico
            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="usuario@empresa.com"
            />
          </label>

          <label>
            Contraseña
            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Ingresa tu contraseña"
            />
          </label>

          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <button type="submit" className="primary-button">
            Ingresar al sistema
          </button>
        </form>

        <div className="login-footer">
          SalesIA Enterprise · Gestión de ventas y analítica
          estadística
        </div>
      </section>
    </main>
  )
}

export default Login
