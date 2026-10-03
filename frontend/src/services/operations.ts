import type {
  InventoryListResponse,
  InventoryMovementCreateRequest,
  InventoryMovementListResponse,
  InventoryMovementRecord,
  SaleCreateRequest,
  SaleListResponse,
  SaleRecord,
} from '../types/api'
import { apiGet, apiPost } from './api'

export interface InventoryFilters {
  page: number
  pageSize: number
  search: string
  status: 'active' | 'inactive' | ''
}

export function listInventory(
  filters: InventoryFilters,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    page: String(filters.page),
    page_size: String(filters.pageSize),
  })
  if (filters.search.trim()) query.set('search', filters.search.trim())
  if (filters.status) query.set('active', String(filters.status === 'active'))
  return apiGet<InventoryListResponse>(`/inventory?${query}`, signal)
}

export function listInventoryMovements(signal?: AbortSignal) {
  return apiGet<InventoryMovementListResponse>(
    '/inventory/movements?page=1&page_size=100',
    signal,
  )
}

export function createInventoryMovement(
  payload: InventoryMovementCreateRequest,
) {
  return apiPost<InventoryMovementRecord>('/inventory/movements', payload)
}

export interface SaleFilters {
  page: number
  pageSize: number
  number: string
}

export function listSales(filters: SaleFilters, signal?: AbortSignal) {
  const query = new URLSearchParams({
    page: String(filters.page),
    page_size: String(filters.pageSize),
  })
  if (filters.number.trim()) query.set('number', filters.number.trim())
  return apiGet<SaleListResponse>(`/sales?${query}`, signal)
}

export function createSale(
  payload: SaleCreateRequest,
  idempotencyKey: string,
) {
  return apiPost<SaleRecord>('/sales', payload, {
    'Idempotency-Key': idempotencyKey,
  })
}
