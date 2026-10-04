import { apiGet, apiPost } from './api'
import type {
  AccessLocationList,
  AuditLogList,
  SecuritySessionList,
} from '../types/api'

interface IpWhoResponse {
  success: boolean
  ip?: string
  latitude?: number
  longitude?: number
  city?: string
  region?: string
  country?: string
  country_code?: string
  connection?: { isp?: string }
  timezone?: { id?: string }
}

export function getSessions(signal?: AbortSignal) {
  return apiGet<SecuritySessionList>('/security/sessions', signal)
}

export function getAccessLocations(signal?: AbortSignal) {
  return apiGet<AccessLocationList>('/security/access-locations', signal)
}

export async function captureLoginLocation() {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 6000)
  try {
    const response = await fetch('https://ipwho.is/', {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return
    const location = await response.json() as IpWhoResponse
    if (
      !location.success || !location.ip ||
      typeof location.latitude !== 'number' ||
      typeof location.longitude !== 'number'
    ) return
    await apiPost<void>('/security/sessions/current/location', {
      ip_address: location.ip,
      latitude: location.latitude,
      longitude: location.longitude,
      city: location.city || null,
      region: location.region || null,
      country: location.country || null,
      country_code: location.country_code || null,
      isp: location.connection?.isp || null,
      timezone: location.timezone?.id || null,
    })
  } catch {
    // La geolocalización por IP es informativa y nunca debe bloquear el acceso.
  } finally {
    window.clearTimeout(timeout)
  }
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
