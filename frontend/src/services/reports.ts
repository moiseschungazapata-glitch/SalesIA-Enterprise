import type {
  ReportDetail,
  ReportGenerateRequest,
  ReportListResponse,
  ReportType,
} from '../types/api'
import { apiDownload, apiGet, apiPost } from './api'

export function listReports(reportType?: ReportType, signal?: AbortSignal) {
  const query = reportType ? `&report_type=${reportType}` : ''
  return apiGet<ReportListResponse>(
    `/reports?page=1&page_size=100${query}`,
    signal,
  )
}

export function getReport(reportId: number, signal?: AbortSignal) {
  return apiGet<ReportDetail>(`/reports/${reportId}`, signal)
}

export function generateReport(payload: ReportGenerateRequest) {
  return apiPost<ReportDetail>('/reports/generate', payload)
}

export async function downloadReport(reportId: number) {
  const { blob, filename } = await apiDownload(
    `/reports/${reportId}/export?format=csv`,
  )
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
}
