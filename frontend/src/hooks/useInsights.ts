import { useCallback, useEffect, useState } from 'react'
import { listInsights } from '../services/insights'
import type { InsightListResponse } from '../types/api'

const emptyInsights: InsightListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 100,
}

function requestMessage(error: unknown) {
  if (error instanceof DOMException && error.name === 'AbortError') return ''
  return error instanceof Error
    ? error.message
    : 'No se pudo cargar el historial de insights.'
}

export function useInsights() {
  const [data, setData] = useState(emptyInsights)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void listInsights(controller.signal)
        .then(setData)
        .catch((requestError: unknown) => {
          const message = requestMessage(requestError)
          if (message) setError(message)
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false)
        })
    }, 0)

    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [reloadKey])

  return { data, loading, error, reload }
}
