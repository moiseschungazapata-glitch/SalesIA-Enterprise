export type PageKey =
  | 'dashboard'
  | 'customers'
  | 'products'
  | 'sales'
  | 'inventory'
  | 'analytics'
  | 'probability'
  | 'insights'
  | 'reports'

export interface NavigationItem {
  key: PageKey
  label: string
  description: string
}

export const navigationItems: NavigationItem[] = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    description: 'Resumen general del negocio',
  },
  {
    key: 'customers',
    label: 'Clientes',
    description: 'Gestión de clientes',
  },
  {
    key: 'products',
    label: 'Productos',
    description: 'Catálogo de productos',
  },
  {
    key: 'sales',
    label: 'Ventas',
    description: 'Gestión comercial',
  },
  {
    key: 'inventory',
    label: 'Inventario',
    description: 'Control de stock',
  },
  {
    key: 'analytics',
    label: 'Analytics',
    description: 'Análisis estadístico',
  },
  {
    key: 'probability',
    label: 'Probabilidad',
    description: 'Probabilidad y Bayes',
  },
  {
    key: 'insights',
    label: 'Insights',
    description: 'Hallazgos comerciales',
  },
  {
    key: 'reports',
    label: 'Reportes',
    description: 'Reportes empresariales',
  },
]
