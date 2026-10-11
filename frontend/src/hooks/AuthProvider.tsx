import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  UNAUTHORIZED_EVENT,
  apiGet,
  apiPost,
  clearAccessToken,
  getAccessToken,
  saveAccessToken,
} from '../services/api'
import type {
  AuthUser,
  LoginResponse,
  SessionUser,
} from '../types/api'
import {
  captureAnonymousVisit,
  captureLoginLocation,
  heartbeatAnonymousVisit,
  heartbeatAuthenticatedSession,
} from '../services/security'
import {
  AuthContext,
  type AuthStatus,
} from './auth-context'

interface AuthProviderProps {
  children: ReactNode
}

function AuthProvider({ children }: AuthProviderProps) {
  const [status, setStatus] = useState<AuthStatus>(() =>
    getAccessToken() ? 'loading' : 'anonymous',
  )
  const [user, setUser] = useState<AuthUser | null>(null)

  useEffect(() => {
    if (!getAccessToken()) void captureAnonymousVisit()
  }, [])

  useEffect(() => {
    if (status === 'loading') return
    const sendHeartbeat = () => {
      if (document.visibilityState === 'hidden') return
      if (status === 'authenticated') void heartbeatAuthenticatedSession()
      else void heartbeatAnonymousVisit()
    }
    const interval = window.setInterval(sendHeartbeat, 30_000)
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') sendHeartbeat()
    }
    document.addEventListener('visibilitychange', handleVisibility)
    return () => {
      window.clearInterval(interval)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [status])

  const logout = useCallback(() => {
    if (getAccessToken()) {
      void apiPost<void>('/auth/logout', {}).catch(() => undefined)
    }
    clearAccessToken()
    setUser(null)
    setStatus('anonymous')
  }, [])

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      return
    }

    const controller = new AbortController()

    void apiGet<SessionUser>('/auth/me', controller.signal)
      .then((sessionUser) => {
        setUser(sessionUser)
        setStatus('authenticated')
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }
        logout()
      })

    return () => controller.abort()
  }, [logout])

  useEffect(() => {
    window.addEventListener(UNAUTHORIZED_EVENT, logout)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, logout)
  }, [logout])

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiPost<LoginResponse>('/auth/login', {
      email,
      password,
    })
    saveAccessToken(response.access_token)
    setUser(response.user)
    setStatus('authenticated')
    void captureLoginLocation()
  }, [])

  const value = useMemo(
    () => ({ status, user, login, logout }),
    [status, user, login, logout],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider
