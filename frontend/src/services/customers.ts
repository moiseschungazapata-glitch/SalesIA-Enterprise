import type {
  CustomerCreateRequest,
  CustomerListResponse,
  CustomerRecord,
  CustomerUpdateRequest,
} from '../types/api'
import { apiGet, apiPatch, apiPost } from './api'

export interface CustomerListFilters {
  page: number
  pageSize: number
  search: string
  status: 'active' | 'inactive' | ''
}

export function listCustomers(
  filters: CustomerListFilters,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    page: String(filters.page),
    page_size: String(filters.pageSize),
  })
  if (filters.search.trim()) {
    query.set('search', filters.search.trim())
  }
  if (filters.status) {
    query.set('active', String(filters.status === 'active'))
  }
  return apiGet<CustomerListResponse>(`/customers?${query}`, signal)
}

export function createCustomer(payload: CustomerCreateRequest) {
  return apiPost<CustomerRecord>('/customers', payload)
}

export function updateCustomer(
  customerId: number,
  payload: CustomerUpdateRequest,
) {
  return apiPatch<CustomerRecord>(`/customers/${customerId}`, payload)
}
