const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api/v1'
).replace(/\/$/, '')

const ACCESS_TOKEN_KEY = 'salesia.access_token'
export const UNAUTHORIZED_EVENT = 'salesia:unauthorized'

interface ApiErrorPayload {
  error?: {
    code?: string
    message?: string
    details?: Record<string, unknown>
  }
}

export class ApiError extends Error {
  status: number
  code: string
  details: Record<string, unknown>

  constructor(
    message: string,
    status: number,
    code = 'HTTP_ERROR',
    details: Record<string, unknown> = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

export function getAccessToken() {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY)
}

export function saveAccessToken(token: string) {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function clearAccessToken() {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY)
}

async function parseResponse(response: Response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    return null
  }

  return response.json() as Promise<unknown>
}

async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers)
  const token = getAccessToken()

  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    throw new ApiError(
      'No se pudo conectar con la API. Verifica que el backend esté iniciado.',
      0,
      'NETWORK_ERROR',
    )
  }

  const payload = await parseResponse(response)

  if (!response.ok) {
    const apiPayload = payload as ApiErrorPayload | null
    const apiError = apiPayload?.error

    if (response.status === 401 && token) {
      clearAccessToken()
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }

    throw new ApiError(
      apiError?.message || `La solicitud falló (${response.status}).`,
      response.status,
      apiError?.code,
      apiError?.details,
    )
  }

  return payload as T
}

export function apiGet<T>(path: string, signal?: AbortSignal) {
  return apiRequest<T>(path, { signal })
}

export function apiPost<T>(
  path: string,
  body: unknown,
  headers?: HeadersInit,
) {
  return apiRequest<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
    headers,
  })
}

export function apiPatch<T>(path: string, body: unknown) {
  return apiRequest<T>(path, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}
