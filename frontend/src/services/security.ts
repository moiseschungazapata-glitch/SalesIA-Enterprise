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

export interface LocationCaptureResult {
  mode: 'precise' | 'ip' | 'unavailable'
  message: string
}

async function getPublicIpLocation(): Promise<IpWhoResponse | null> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 6000)
  try {
    const response = await fetch('https://ipwho.is/', {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return null
    const location = await response.json() as IpWhoResponse
    return location.success ? location : null
  } catch {
    return null
  } finally {
    window.clearTimeout(timeout)
  }
}

function getDeviceLocation(): Promise<GeolocationPosition | null> {
  if (!navigator.geolocation || !window.isSecureContext) {
    return Promise.resolve(null)
  }
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      resolve,
      () => resolve(null),
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
      },
    )
  })
}

export async function captureLoginLocation(): Promise<LocationCaptureResult> {
  const [ipLocation, deviceLocation] = await Promise.all([
    getPublicIpLocation(),
    getDeviceLocation(),
  ])

  const precise = deviceLocation?.coords
  const latitude = precise?.latitude ?? ipLocation?.latitude
  const longitude = precise?.longitude ?? ipLocation?.longitude
  if (typeof latitude !== 'number' || typeof longitude !== 'number') {
    return {
      mode: 'unavailable',
      message: window.isSecureContext
        ? 'No fue posible obtener la ubicación. Revisa el permiso del navegador.'
        : 'La ubicación precisa requiere abrir SalesIA mediante HTTPS.',
    }
  }

  try {
    await apiPost<void>('/security/sessions/current/location', {
      ip_address: ipLocation?.ip || null,
      latitude,
      longitude,
      city: ipLocation?.city || null,
      region: ipLocation?.region || null,
      country: ipLocation?.country || null,
      country_code: ipLocation?.country_code || null,
      isp: ipLocation?.connection?.isp || null,
      timezone: ipLocation?.timezone?.id || null,
      source: precise ? 'device_location' : 'public_ip',
      accuracy_m: precise?.accuracy ?? null,
    })
  } catch {
    return { mode: 'unavailable', message: 'No fue posible guardar la ubicación de esta sesión.' }
  }

  return precise
    ? {
        mode: 'precise',
        message: `Ubicación precisa actualizada (margen aproximado: ${Math.round(precise.accuracy)} m).`,
      }
    : {
        mode: 'ip',
        message: window.isSecureContext
          ? 'No se autorizó la ubicación precisa; se conservó la estimación por IP.'
          : 'Se conservó la estimación por IP. Para usar GPS abre SalesIA mediante HTTPS.',
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
