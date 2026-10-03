import { useCallback, useEffect, useState } from 'react'
import {
  listUsers,
  type UserListFilters,
} from '../services/users'
import type { UserListResponse } from '../types/api'

const emptyPage: UserListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
}

export function useUsers(filters: UserListFilters) {
  const { page, pageSize, role, search, status } = filters
  const [data, setData] = useState<UserListResponse>(emptyPage)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  const reload = useCallback(() => {
    setReloadKey((value) => value + 1)
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(
      () => {
        setLoading(true)
        setError('')

        void listUsers(
          { page, pageSize, role, search, status },
          controller.signal,
        )
          .then(setData)
          .catch((requestError: unknown) => {
            if (
              requestError instanceof DOMException &&
              requestError.name === 'AbortError'
            ) {
              return
            }
            setError(
              requestError instanceof Error
                ? requestError.message
                : 'No se pudieron cargar los usuarios.',
            )
          })
          .finally(() => {
            if (!controller.signal.aborted) {
              setLoading(false)
            }
          })
      },
      search ? 300 : 0,
    )

    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [
    page,
    pageSize,
    role,
    search,
    status,
    reloadKey,
  ])

  return { data, loading, error, reload }
}
