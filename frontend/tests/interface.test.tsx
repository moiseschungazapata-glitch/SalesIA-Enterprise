import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import FormModal from '../src/components/FormModal'
import Sidebar from '../src/components/Sidebar'

describe('interacción del dashboard', () => {
  it('navega, cierra el menú móvil y respeta el rol', async () => {
    const user = userEvent.setup()
    const onNavigate = vi.fn()
    const onClose = vi.fn()
    render(
      <Sidebar
        activePage="sales"
        role="seller"
        onNavigate={onNavigate}
        onLogout={vi.fn()}
        mobileOpen
        onClose={onClose}
      />,
    )

    expect(screen.queryByRole('button', { name: 'Usuarios' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Inventario' }))
    expect(onNavigate).toHaveBeenCalledWith('inventory')
    expect(onClose).toHaveBeenCalled()
  })

  it('presenta formularios como diálogo y los cierra con Escape', () => {
    const onClose = vi.fn()
    const { unmount } = render(
      <FormModal
        eyebrow="NUEVO REGISTRO"
        title="Crear producto"
        description="Completa los datos"
        onClose={onClose}
      >
        <input aria-label="Nombre del producto" />
      </FormModal>,
    )

    expect(screen.getByRole('dialog', { name: 'Crear producto' })).toBeInTheDocument()
    expect(document.body.style.overflow).toBe('hidden')
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledOnce()
    unmount()
    expect(document.body.style.overflow).toBe('')
  })

  it('no permite cerrar un formulario durante una operación', () => {
    const onClose = vi.fn()
    render(
      <FormModal eyebrow="VENTA" title="Registrar venta" onClose={onClose} closeDisabled>
        <span>Procesando</span>
      </FormModal>,
    )
    fireEvent.keyDown(document, { key: 'Escape' })
    fireEvent.mouseDown(screen.getByText('Procesando').closest('.form-modal-backdrop')!)
    expect(onClose).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Cerrar ventana' })).toBeDisabled()
  })
})
