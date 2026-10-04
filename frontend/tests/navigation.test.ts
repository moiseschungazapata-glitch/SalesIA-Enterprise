import { describe, expect, it } from 'vitest'
import {
  canAccessPage,
  getDefaultPage,
  getNavigationItems,
  getPageByPath,
  pagePaths,
} from '../src/app/navigation'

describe('reglas de navegación por rol', () => {
  it('reserva usuarios para administración', () => {
    expect(canAccessPage('administrator', 'users')).toBe(true)
    expect(canAccessPage('manager', 'users')).toBe(false)
    expect(canAccessPage('seller', 'users')).toBe(false)
  })

  it('limita al vendedor a la operación y seguridad', () => {
    expect(getNavigationItems('seller').map((item) => item.key)).toEqual([
      'sales',
      'customers',
      'products',
      'inventory',
      'security',
    ])
    expect(getDefaultPage('seller')).toBe('sales')
    expect(getDefaultPage('manager')).toBe('dashboard')
  })

  it('mantiene una ruta reversible para cada página', () => {
    for (const [page, path] of Object.entries(pagePaths)) {
      expect(getPageByPath(path)).toBe(page)
    }
    expect(getPageByPath('/ruta-inexistente')).toBeUndefined()
  })
})
