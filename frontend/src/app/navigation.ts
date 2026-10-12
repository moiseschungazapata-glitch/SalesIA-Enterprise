export type UserRole =
  | 'administrator'
  | 'seller'
  | 'manager'
  | 'analyst'
  | 'warehouse'

export type PageKey =
  | 'dashboard'
  | 'sales'
  | 'payments'
  | 'sellers'
  | 'orders'
  | 'customers'
  | 'products'
  | 'inventory'
  | 'analytics'
  | 'probability'
  | 'insights'
  | 'reports'
  | 'security'
  | 'users'
  | 'settings'

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
  'analyst',
  'warehouse',
]

export const navigationItems: NavigationItem[] = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    description: 'Resumen comercial del negocio',
    roles: ['administrator', 'manager'],
  },
  {
    key: 'orders',
    label: 'Pedidos',
    description: 'Preparación y conversión de pedidos',
    roles: ['administrator', 'seller', 'manager'],
  },
  {
    key: 'sales',
    label: 'Ventas',
    description: 'Historial y registro de ventas',
    roles: ['administrator', 'seller', 'manager'],
  },
  {
    key: 'payments',
    label: 'Pagos',
    description: 'Cobros, saldos y devoluciones',
    roles: ['administrator', 'seller', 'manager'],
  },
  {
    key: 'sellers',
    label: 'Vendedores',
    description: 'Metas, zonas y comisiones',
    roles: ['administrator', 'manager'],
  },
  {
    key: 'customers',
    label: 'Clientes',
    description: 'Consulta y gestión de clientes',
    roles: ['administrator', 'seller', 'manager'],
  },
  {
    key: 'products',
    label: 'Productos',
    description: 'Catálogo de productos y categorías',
    roles: ['administrator', 'seller', 'manager', 'warehouse'],
  },
  {
    key: 'inventory',
    label: 'Inventario',
    description: 'Existencias y movimientos',
    roles: ['administrator', 'seller', 'manager', 'warehouse'],
  },
  {
    key: 'analytics',
    label: 'Analytics',
    description: 'Media, mediana y variables estadísticas',
    roles: ['administrator', 'manager', 'analyst'],
  },
  {
    key: 'probability',
    label: 'Probabilidad',
    description: 'Eventos, variables aleatorias y Bayes',
    roles: ['administrator', 'manager', 'analyst'],
  },
  {
    key: 'insights',
    label: 'Insights',
    description: 'Hallazgos explicables e historial',
    roles: ['administrator', 'manager', 'analyst'],
  },
  {
    key: 'reports',
    label: 'Reportes',
    description: 'Reportes, exportación e impresión',
    roles: ['administrator', 'manager', 'analyst'],
  },
  {
    key: 'security',
    label: 'Seguridad',
    description: 'Sesiones activas y registro de auditoría',
    roles: allRoles,
  },
  {
    key: 'users',
    label: 'Usuarios',
    description: 'Usuarios, roles y estados',
    roles: ['administrator'],
  },
  {
    key: 'settings',
    label: 'Configuración',
    description: 'IGV, precios y descuentos',
    roles: ['administrator'],
  },
]

export const roleLabels: Record<UserRole, string> = {
  administrator: 'Administrador',
  seller: 'Vendedor',
  manager: 'Gerente',
  analyst: 'Analista',
  warehouse: 'Almacén',
}

export const pagePaths: Record<PageKey, string> = {
  dashboard: '/dashboard',
  sales: '/ventas',
  payments: '/pagos',
  sellers: '/vendedores',
  orders: '/pedidos',
  customers: '/clientes',
  products: '/productos',
  inventory: '/inventario',
  analytics: '/analytics',
  probability: '/probabilidad',
  insights: '/insights',
  reports: '/reportes',
  security: '/seguridad',
  users: '/usuarios',
  settings: '/configuracion',
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
  if (role === 'seller') return 'sales'
  if (role === 'analyst') return 'analytics'
  if (role === 'warehouse') return 'inventory'
  return 'dashboard'
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
