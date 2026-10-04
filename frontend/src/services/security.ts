import { apiGet, apiPost } from './api'
import type {
  AuditLogList,
  SecuritySessionList,
} from '../types/api'

export function getSessions(signal?: AbortSignal) {
  return apiGet<SecuritySessionList>('/security/sessions', signal)
}

export function revokeSession(sessionId: number) {
  return apiPost<{ revoked: number }>(`/security/sessions/${sessionId}/revoke`, {})
}

export function revokeOtherSessions() {
  return apiPost<{ revoked: number }>('/security/sessions/revoke-others', {})
}

export function getAuditLogs(signal?: AbortSignal) {
  return apiGet<AuditLogList>('/security/audit-logs?page=1&page_size=50', signal)
}
