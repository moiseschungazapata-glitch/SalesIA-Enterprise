import type { UserRole } from '../app/navigation'
import type {
  UserCreateRequest,
  UserListResponse,
  UserRecord,
  UserUpdateRequest,
} from '../types/api'
import { apiGet, apiPatch, apiPost } from './api'

export interface UserListFilters {
  page: number
  pageSize: number
  search: string
  role: UserRole | ''
  status: 'active' | 'inactive' | ''
}

export function listUsers(
  filters: UserListFilters,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    page: String(filters.page),
    page_size: String(filters.pageSize),
  })

  if (filters.search.trim()) {
    query.set('search', filters.search.trim())
  }
  if (filters.role) {
    query.set('role', filters.role)
  }
  if (filters.status) {
    query.set('active', String(filters.status === 'active'))
  }

  return apiGet<UserListResponse>(`/users?${query}`, signal)
}

export function createUser(payload: UserCreateRequest) {
  return apiPost<UserRecord>('/users', payload)
}

export function updateUser(
  userId: number,
  payload: UserUpdateRequest,
) {
  return apiPatch<UserRecord>(`/users/${userId}`, payload)
}
