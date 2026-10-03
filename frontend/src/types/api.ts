import type { UserRole } from '../app/navigation'

export interface AuthUser {
  id: number
  name: string
  email: string
  role: UserRole
}

export interface SessionUser extends AuthUser {
  active: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  user: AuthUser
}

export interface UserRecord extends SessionUser {
  created_at: string
  updated_at: string
}

export interface UserListResponse {
  items: UserRecord[]
  total: number
  page: number
  page_size: number
}

export interface UserCreateRequest {
  name: string
  email: string
  password: string
  role: UserRole
}

export interface UserUpdateRequest {
  name?: string
  email?: string
  role?: UserRole
  active?: boolean
  new_password?: string
}

export type CustomerType = 'person' | 'company'
export type DocumentType = 'DNI' | 'RUC'

export interface CustomerRecord {
  id: number
  customer_type: CustomerType
  document_type: DocumentType
  document_number: string
  name: string
  phone: string | null
  email: string | null
  address: string | null
  active: boolean
  created_at: string
  updated_at: string
}

export interface CustomerListResponse {
  items: CustomerRecord[]
  total: number
  page: number
  page_size: number
}

export interface CustomerCreateRequest {
  customer_type: CustomerType
  document_type: DocumentType
  document_number: string
  name: string
  phone?: string | null
  email?: string | null
  address?: string | null
}

export interface CustomerUpdateRequest {
  name?: string
  phone?: string | null
  email?: string | null
  address?: string | null
  active?: boolean
}

export interface CategoryRecord {
  id: number
  name: string
  description: string | null
  active: boolean
  created_at: string
  updated_at: string
}

export interface CategoryListResponse {
  items: CategoryRecord[]
  total: number
  page: number
  page_size: number
}

export interface CategoryCreateRequest {
  name: string
  description?: string | null
}

export interface CategoryUpdateRequest {
  name?: string
  description?: string | null
  active?: boolean
}

export interface ProductRecord {
  id: number
  sku: string
  name: string
  description: string | null
  category_id: number
  category_name: string
  unit_price: string
  stock: number
  active: boolean
  created_at: string
  updated_at: string
}

export interface ProductListResponse {
  items: ProductRecord[]
  total: number
  page: number
  page_size: number
}

export interface ProductCreateRequest {
  sku: string
  name: string
  description?: string | null
  category_id: number
  unit_price: string
  initial_stock: number
}

export interface ProductUpdateRequest {
  sku?: string
  name?: string
  description?: string | null
  category_id?: number
  unit_price?: string
  active?: boolean
}
