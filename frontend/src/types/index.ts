export interface Customer {
  id: number
  name: string
  email: string
  phone: string
  city: string
  purchases: number
  status: 'Activo' | 'Inactivo'
}

export interface Product {
  id: number
  name: string
  category: string
  price: number
  stock: number
  sold: number
  status: 'Disponible' | 'Stock bajo' | 'Agotado'
}

export interface Sale {
  id: string
  customer: string
  seller: string
  date: string
  items: number
  total: number
  payment: 'Completado' | 'Pendiente'
}

export interface InventoryItem {
  id: number
  product: string
  category: string
  stock: number
  minimum: number
  movement: string
  updated: string
}

export interface Insight {
  id: number
  title: string
  description: string
  metric: string
  category: 'Ventas' | 'Clientes' | 'Inventario' | 'Productos'
  type: 'positive' | 'warning' | 'info'
}
