import type {
  InsightGenerationRequest,
  InsightGenerationResponse,
  InsightListResponse,
} from '../types/api'
import { apiGet, apiPost } from './api'

export function listInsights(signal?: AbortSignal) {
  return apiGet<InsightListResponse>(
    '/insights?page=1&page_size=100',
    signal,
  )
}

export function generateInsights(payload: InsightGenerationRequest) {
  return apiPost<InsightGenerationResponse>(
    '/insights/generate',
    payload,
  )
}
