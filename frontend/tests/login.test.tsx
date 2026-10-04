import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Login from '../src/modules/auth/Login'
import ThemeProvider from '../src/theme/ThemeProvider'

const login = vi.fn()

vi.mock('../src/hooks/useAuth', () => ({
  useAuth: () => ({ login }),
}))

function renderLogin() {
  return render(
    <ThemeProvider>
      <Login />
    </ThemeProvider>,
  )
}

describe('formulario de acceso', () => {
  beforeEach(() => login.mockReset())

  it('muestra y vuelve a ocultar la contraseña', async () => {
    const user = userEvent.setup()
    renderLogin()
    const password = screen.getByLabelText('Contraseña')

    expect(password).toHaveAttribute('type', 'password')
    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }))
    expect(password).toHaveAttribute('type', 'text')
    await user.click(screen.getByRole('button', { name: 'Ocultar contraseña' }))
    expect(password).toHaveAttribute('type', 'password')
  })

  it('valida la longitud antes de solicitar acceso', async () => {
    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText('Correo electrónico'), 'admin@salesia.pe')
    await user.type(screen.getByLabelText('Contraseña'), 'corta')
    await user.click(screen.getByRole('button', { name: 'Ingresar al sistema' }))

    expect(screen.getByRole('alert')).toHaveTextContent('al menos 12 caracteres')
    expect(login).not.toHaveBeenCalled()
  })

  it('envía credenciales válidas y normaliza el correo', async () => {
    const user = userEvent.setup()
    login.mockResolvedValue(undefined)
    renderLogin()
    await user.type(screen.getByLabelText('Correo electrónico'), ' admin@salesia.pe ')
    await user.type(screen.getByLabelText('Contraseña'), 'ClaveSegura-123')
    await user.click(screen.getByRole('button', { name: 'Ingresar al sistema' }))

    expect(login).toHaveBeenCalledWith('admin@salesia.pe', 'ClaveSegura-123')
  })

  it('cambia el tema y conserva la preferencia', async () => {
    const user = userEvent.setup()
    renderLogin()
    await user.click(screen.getByRole('button', { name: 'Cambiar a modo oscuro' }))

    expect(document.documentElement).toHaveAttribute('data-theme', 'dark')
    expect(window.localStorage.getItem('salesia.theme')).toBe('dark')
  })
})
