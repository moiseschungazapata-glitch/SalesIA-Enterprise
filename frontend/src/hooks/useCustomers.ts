import { useCallback, useEffect, useState } from 'react'
import {
  listCustomers,
  type CustomerListFilters,
} from '../services/customers'
import type { CustomerListResponse } from '../types/api'

const emptyPage: CustomerListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
}

export function useCustomers(filters: CustomerListFilters) {
  const { page, pageSize, search, status } = filters
  const [data, setData] = useState<CustomerListResponse>(emptyPage)
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
        void listCustomers(
          { page, pageSize, search, status },
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
                : 'No se pudieron cargar los clientes.',
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
  }, [page, pageSize, reloadKey, search, status])

  return { data, loading, error, reload }
}
