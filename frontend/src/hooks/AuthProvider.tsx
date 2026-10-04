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
