import type { PaymentListResponse, PaymentMethod, PaymentRecord } from '../types/api'
import { apiGet, apiPost } from './api'

export const listPayments = (status = '', signal?: AbortSignal) =>
  apiGet<PaymentListResponse>(`/payments?page=1&page_size=100${status ? `&status=${status}` : ''}`, signal)

export const createPayment = (payload: {
  sale_id: number
  method: PaymentMethod
  amount: string
  reference?: string | null
}) => apiPost<PaymentRecord>('/payments', payload)

export const reversePayment = (id: number, action: 'cancel' | 'refund', reason: string) =>
  apiPost<PaymentRecord>(`/payments/${id}/${action}`, { reason })
