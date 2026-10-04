import type { DashboardSummary } from '../types/api'
import { apiGet } from './api'

export interface DashboardFilters {
  dateFrom: string
  dateTo: string
  branch: 'main'
  sellerId: string
  categoryId: string
}

export function getDashboardSummary(
  filters: DashboardFilters,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    date_from: filters.dateFrom,
    date_to: filters.dateTo,
    branch: filters.branch,
  })
  if (filters.sellerId) query.set('seller_id', filters.sellerId)
  if (filters.categoryId) query.set('category_id', filters.categoryId)
  return apiGet<DashboardSummary>(`/dashboard/summary?${query}`, signal)
}
