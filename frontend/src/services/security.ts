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

const ANONYMOUS_VISIT_KEY = 'salesia.anonymous_visit_mode_v2'
const ANONYMOUS_PAYLOAD_KEY = 'salesia.anonymous_visit_payload_v1'
const AUTHENTICATED_PAYLOAD_KEY = 'salesia.authenticated_location_payload_v1'

interface AnonymousVisitPayload {
  ip_address?: string | null
  latitude: number
  longitude: number
  city: string | null
  region: string | null
  country: string | null
  country_code: string | null
  isp: string | null
  timezone: string | null
  source: 'public_ip' | 'device_location'
  accuracy_m: number | null
  location_active: boolean
  heartbeat?: boolean
}

async function locationPermissionActive(fallback = false) {
  if (!navigator.permissions?.query) return fallback
  try {
    const permission = await navigator.permissions.query({ name: 'geolocation' })
    return permission.state === 'granted'
  } catch {
    return fallback
  }
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

export async function captureAnonymousVisit(
  retryPrecise = false,
): Promise<LocationCaptureResult> {
  const savedMode = sessionStorage.getItem(ANONYMOUS_VISIT_KEY)
  const savedPayload = sessionStorage.getItem(ANONYMOUS_PAYLOAD_KEY)
  if (savedMode === 'precise' && savedPayload) {
    return { mode: 'precise', message: 'La ubicación precisa ya fue registrada.' }
  }
  if (savedMode === 'ip' && savedPayload && !retryPrecise) {
    return { mode: 'ip', message: 'Se registró una estimación por IP.' }
  }
  const [location, deviceLocation] = await Promise.all([
    getPublicIpLocation(),
    getDeviceLocation(),
  ])
  const precise = deviceLocation?.coords
  const latitude = precise?.latitude ?? location?.latitude
  const longitude = precise?.longitude ?? location?.longitude
  if (
    typeof latitude !== 'number' ||
    typeof longitude !== 'number'
  ) {
    return {
      mode: 'unavailable',
      message: 'No fue posible obtener la ubicación de este dispositivo.',
    }
  }

  try {
    const payload: AnonymousVisitPayload = {
      latitude,
      longitude,
      city: location?.city || null,
      region: location?.region || null,
      country: location?.country || null,
      country_code: location?.country_code || null,
      isp: location?.connection?.isp || null,
      timezone: location?.timezone?.id || null,
      source: precise ? 'device_location' : 'public_ip',
      accuracy_m: precise?.accuracy ?? null,
      location_active: precise
        ? await locationPermissionActive(true)
        : false,
    }
    await apiPost<void>('/public/visits', payload)
    sessionStorage.setItem(ANONYMOUS_PAYLOAD_KEY, JSON.stringify(payload))
    const mode = precise ? 'precise' : 'ip'
    sessionStorage.setItem(ANONYMOUS_VISIT_KEY, mode)
    return precise
      ? {
          mode: 'precise',
          message: `Ubicación precisa compartida (margen aproximado: ${Math.round(precise.accuracy)} m).`,
        }
      : {
          mode: 'ip',
          message: 'El navegador no autorizó la ubicación precisa; se registró una estimación por IP.',
        }
  } catch {
    // Tracking must never prevent the public login page from working.
    return {
      mode: 'unavailable',
      message: 'No fue posible guardar la ubicación en este momento.',
    }
  }
}

export async function heartbeatAnonymousVisit() {
  const rawPayload = sessionStorage.getItem(ANONYMOUS_PAYLOAD_KEY)
  if (!rawPayload) return
  try {
    const payload = JSON.parse(rawPayload) as AnonymousVisitPayload
    payload.location_active = await locationPermissionActive(
      payload.source === 'device_location',
    )
    if (payload.location_active) {
      const current = await getDeviceLocation(10_000, 20_000)
      if (current) {
        payload.latitude = current.coords.latitude
        payload.longitude = current.coords.longitude
        payload.accuracy_m = current.coords.accuracy
        payload.source = 'device_location'
      }
    }
    payload.heartbeat = true
    await apiPost<void>('/public/visits', payload)
    sessionStorage.setItem(ANONYMOUS_PAYLOAD_KEY, JSON.stringify(payload))
  } catch {
    // Presence updates are best-effort and must not interrupt the login.
  }
}

export async function heartbeatAuthenticatedSession() {
  try {
    const locationActive = await locationPermissionActive(false)
    const rawPayload = sessionStorage.getItem(AUTHENTICATED_PAYLOAD_KEY)
    if (locationActive && rawPayload) {
      const payload = JSON.parse(rawPayload) as AnonymousVisitPayload
      const current = await getDeviceLocation(10_000, 20_000)
      if (current) {
        payload.latitude = current.coords.latitude
        payload.longitude = current.coords.longitude
        payload.accuracy_m = current.coords.accuracy
        payload.source = 'device_location'
        payload.location_active = true
        await apiPost<void>('/security/sessions/current/location', payload)
        sessionStorage.setItem(AUTHENTICATED_PAYLOAD_KEY, JSON.stringify(payload))
        return
      }
    }
    await apiPost<void>('/security/sessions/current/heartbeat', {
      location_active: locationActive,
    })
  } catch {
    // Normal authorization handling will take care of expired sessions.
  }
}

function getDeviceLocation(
  timeout = 15000,
  maximumAge = 0,
): Promise<GeolocationPosition | null> {
  if (!navigator.geolocation || !window.isSecureContext) {
    return Promise.resolve(null)
  }
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      resolve,
      () => resolve(null),
      {
        enableHighAccuracy: true,
        timeout,
        maximumAge,
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
    const payload: AnonymousVisitPayload = {
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
      location_active: precise
        ? await locationPermissionActive(true)
        : false,
    }
    await apiPost<void>('/security/sessions/current/location', payload)
    sessionStorage.setItem(AUTHENTICATED_PAYLOAD_KEY, JSON.stringify(payload))
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
