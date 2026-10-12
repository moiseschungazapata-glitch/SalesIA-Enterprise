import type { SellerListResponse, SellerRecord, SellerUpdateRequest } from '../types/api'
import { apiGet, apiPut } from './api'

export const listSellers = (signal?: AbortSignal) =>
  apiGet<SellerListResponse>('/sellers', signal)

export const updateSeller = (userId: number, payload: SellerUpdateRequest) =>
  apiPut<SellerRecord>(`/sellers/${userId}`, payload)
