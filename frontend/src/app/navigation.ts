export type UserRole =
  | 'administrator'
  | 'seller'
  | 'manager'

export type PageKey =
  | 'dashboard'
  | 'sales'
  | 'customers'
  | 'products'
  | 'inventory'
  | 'users'

export interface NavigationItem {
  key: PageKey
  label: string
  description: string
  roles: UserRole[]
}

const allRoles: UserRole[] = [
  'administrator',
  'seller',
  'manager',
]

export const navigationItems: NavigationItem[] = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    description: 'Resumen comercial del negocio',
    roles: ['administrator', 'manager'],
  },
  {
    key: 'sales',
    label: 'Ventas',
    description: 'Historial y registro de ventas',
    roles: allRoles,
  },
  {
    key: 'customers',
    label: 'Clientes',
    description: 'Consulta y gestión de clientes',
    roles: allRoles,
  },
  {
    key: 'products',
    label: 'Productos',
    description: 'Catálogo de productos y categorías',
    roles: allRoles,
  },
  {
    key: 'inventory',
    label: 'Inventario',
    description: 'Existencias y movimientos',
    roles: allRoles,
  },
  {
    key: 'users',
    label: 'Usuarios',
    description: 'Usuarios, roles y estados',
    roles: ['administrator'],
  },
]

export const roleLabels: Record<UserRole, string> = {
  administrator: 'Administrador',
  seller: 'Vendedor',
  manager: 'Gerente',
}

export const pagePaths: Record<PageKey, string> = {
  dashboard: '/dashboard',
  sales: '/ventas',
  customers: '/clientes',
  products: '/productos',
  inventory: '/inventario',
  users: '/usuarios',
}

const pathPages = Object.fromEntries(
  Object.entries(pagePaths).map(([page, path]) => [path, page]),
) as Record<string, PageKey>

export function getNavigationItems(role: UserRole) {
  return navigationItems.filter((item) =>
    item.roles.includes(role),
  )
}

export function getDefaultPage(role: UserRole): PageKey {
  return role === 'seller' ? 'sales' : 'dashboard'
}

export function canAccessPage(
  role: UserRole,
  page: PageKey,
) {
  return navigationItems.some(
    (item) =>
      item.key === page && item.roles.includes(role),
  )
}

export function getPageByPath(pathname: string) {
  return pathPages[pathname]
}
