import type { AccessLocation } from '../types/api'

const ACCESS_COLORS = [
  '#2563eb',
  '#16a34a',
  '#9333ea',
  '#e11d48',
  '#0891b2',
  '#ea580c',
  '#4f46e5',
  '#0d9488',
  '#c026d3',
  '#ca8a04',
  '#0284c7',
  '#65a30d',
]

export function describeDevice(userAgent: string | null) {
  if (!userAgent) return 'Dispositivo no identificado'

  let browser = 'Navegador web'
  if (/Edg\//i.test(userAgent)) browser = 'Edge'
  else if (/OPR\//i.test(userAgent)) browser = 'Opera'
  else if (/SamsungBrowser\//i.test(userAgent)) browser = 'Samsung Internet'
  else if (/CriOS|Chrome\//i.test(userAgent)) browser = 'Chrome'
  else if (/FxiOS|Firefox\//i.test(userAgent)) browser = 'Firefox'
  else if (/Safari\//i.test(userAgent)) browser = 'Safari'

  let device = 'Dispositivo desconocido'
  if (/iPad/i.test(userAgent)) device = 'iPad'
  else if (/iPhone/i.test(userAgent)) device = 'iPhone'
  else if (/Android/i.test(userAgent)) device = 'Android'
  else if (/Windows/i.test(userAgent)) device = 'Windows'
  else if (/Macintosh|Mac OS/i.test(userAgent)) device = 'macOS'
  else if (/Linux/i.test(userAgent)) device = 'Linux'

  return `${browser} · ${device}`
}

export function accessIdentityKey(item: AccessLocation) {
  return item.is_anonymous
    ? `device:${item.ip_address || 'unknown'}:${item.user_agent || 'unknown'}`
    : `user:${item.user_id ?? item.user_email}`
}

export function accessDisplayName(item: AccessLocation) {
  return item.is_anonymous ? describeDevice(item.user_agent) : item.user_name
}

export function accessColor(item: AccessLocation) {
  const key = accessIdentityKey(item)
  let hash = 0
  for (let index = 0; index < key.length; index += 1) {
    hash = ((hash << 5) - hash + key.charCodeAt(index)) | 0
  }
  return ACCESS_COLORS[Math.abs(hash) % ACCESS_COLORS.length]
}
