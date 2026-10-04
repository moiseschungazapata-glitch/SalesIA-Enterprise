import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  ApiError,
  UNAUTHORIZED_EVENT,
  apiGet,
  apiPost,
  getAccessToken,
  saveAccessToken,
} from '../src/services/api'

afterEach(() => vi.unstubAllGlobals())

describe('cliente HTTP', () => {
  it('envía token y cuerpo JSON', async () => {
    saveAccessToken('token-seguro')
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ id: 7 }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiPost('/customers', { name: 'Cliente' })).resolves.toEqual({ id: 7 })
    const [, request] = fetchMock.mock.calls[0]
    expect(new Headers(request.headers).get('Authorization')).toBe('Bearer token-seguro')
    expect(new Headers(request.headers).get('Content-Type')).toBe('application/json')
  })

  it('elimina la sesión y avisa a la aplicación ante un 401', async () => {
    saveAccessToken('token-vencido')
    const unauthorized = vi.fn()
    window.addEventListener(UNAUTHORIZED_EVENT, unauthorized, { once: true })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: 'UNAUTHORIZED', message: 'Sesión vencida' } }), {
        status: 401,
        headers: { 'content-type': 'application/json' },
      }),
    ))

    await expect(apiGet('/auth/me')).rejects.toMatchObject({
      name: 'ApiError',
      status: 401,
      code: 'UNAUTHORIZED',
    })
    expect(getAccessToken()).toBeNull()
    expect(unauthorized).toHaveBeenCalledOnce()
  })

  it('convierte fallas de red en un error entendible', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')))
    await expect(apiGet('/health')).rejects.toEqual(
      expect.objectContaining<ApiError>({ status: 0, code: 'NETWORK_ERROR' }),
    )
  })
})
