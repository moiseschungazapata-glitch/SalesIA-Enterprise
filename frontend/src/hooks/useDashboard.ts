import { useCallback, useEffect, useState } from 'react'
import {
  getDashboardSummary,
  type DashboardFilters,
} from '../services/dashboard'
import type { DashboardSummary } from '../types/api'

function requestMessage(error: unknown) {
  if (error instanceof DOMException && error.name === 'AbortError') return ''
  return error instanceof Error
    ? error.message
    : 'No se pudo cargar el resumen del dashboard.'
}

export function useDashboard(filters: DashboardFilters) {
  const { branch, categoryId, dateFrom, dateTo, sellerId } = filters
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void getDashboardSummary(
        { branch, categoryId, dateFrom, dateTo, sellerId },
        controller.signal,
      ).then(setData).catch((requestError: unknown) => {
        const message = requestMessage(requestError)
        if (message) setError(message)
      }).finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    }, 0)
    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [branch, categoryId, dateFrom, dateTo, reloadKey, sellerId])

  return { data, loading, error, reload }
}
