import { useCallback, useEffect, useState } from 'react'
import { listReports } from '../services/reports'
import type { ReportListResponse, ReportType } from '../types/api'

const emptyReports: ReportListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 100,
}

export function useReports(reportType?: ReportType) {
  const [data, setData] = useState(emptyReports)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void listReports(reportType, controller.signal)
        .then(setData)
        .catch((requestError: unknown) => {
          if (requestError instanceof DOMException && requestError.name === 'AbortError') return
          setError(
            requestError instanceof Error
              ? requestError.message
              : 'No se pudo cargar el historial de reportes.',
          )
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false)
        })
    }, 0)
    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [reloadKey, reportType])

  return { data, loading, error, reload }
}
