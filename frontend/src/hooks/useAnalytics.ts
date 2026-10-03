import { useCallback, useEffect, useState } from 'react'
import {
  listAnalysisHistory,
  listStatisticalVariables,
} from '../services/analytics'
import type {
  AnalysisHistoryResponse,
  StatisticalVariableDefinition,
} from '../types/api'

const emptyHistory: AnalysisHistoryResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 50,
}

function requestMessage(error: unknown, fallback: string) {
  if (error instanceof DOMException && error.name === 'AbortError') return ''
  return error instanceof Error ? error.message : fallback
}

export function useAnalyticsMetadata() {
  const [variables, setVariables] = useState<StatisticalVariableDefinition[]>([])
  const [history, setHistory] = useState<AnalysisHistoryResponse>(emptyHistory)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void Promise.all([
        listStatisticalVariables(controller.signal),
        listAnalysisHistory(controller.signal),
      ])
        .then(([variableData, historyData]) => {
          setVariables(variableData)
          setHistory(historyData)
        })
        .catch((requestError: unknown) => {
          const message = requestMessage(
            requestError,
            'No se pudo cargar la información estadística.',
          )
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

  return { variables, history, loading, error, reload }
}
