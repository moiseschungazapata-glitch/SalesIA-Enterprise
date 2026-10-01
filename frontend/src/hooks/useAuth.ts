import { useState } from 'react'

export function useAuth() {
  const [authenticated, setAuthenticated] = useState(false)

  const login = () => {
    setAuthenticated(true)
  }

  const logout = () => {
    setAuthenticated(false)
  }

  return {
    authenticated,
    login,
    logout,
  }
}
