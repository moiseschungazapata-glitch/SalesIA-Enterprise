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
