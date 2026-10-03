import { useCallback, useEffect, useState } from 'react'
import {
  listInventory,
  listInventoryMovements,
  listSales,
  type InventoryFilters,
  type SaleFilters,
} from '../services/operations'
import type {
  InventoryListResponse,
  InventoryMovementListResponse,
  SaleListResponse,
} from '../types/api'

const emptyInventory: InventoryListResponse = {
  items: [], total: 0, page: 1, page_size: 100,
}
const emptyMovements: InventoryMovementListResponse = {
  items: [], total: 0, page: 1, page_size: 100,
}
const emptySales: SaleListResponse = {
  items: [], total: 0, page: 1, page_size: 20,
}

function requestMessage(error: unknown, fallback: string) {
  if (error instanceof DOMException && error.name === 'AbortError') return ''
  return error instanceof Error ? error.message : fallback
}

export function useInventory(filters: InventoryFilters) {
  const { page, pageSize, search, status } = filters
  const [data, setData] = useState<InventoryListResponse>(emptyInventory)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void listInventory(
        { page, pageSize, search, status }, controller.signal,
      ).then(setData).catch((requestError: unknown) => {
        const message = requestMessage(
          requestError, 'No se pudo cargar el inventario.',
        )
        if (message) setError(message)
      }).finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    }, search ? 300 : 0)
    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [page, pageSize, reloadKey, search, status])

  return { data, loading, error, reload }
}

export function useInventoryMovements(enabled: boolean) {
  const [data, setData] = useState<InventoryMovementListResponse>(emptyMovements)
  const [loading, setLoading] = useState(enabled)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    if (!enabled) return
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void listInventoryMovements(controller.signal).then(setData)
        .catch((requestError: unknown) => {
          const message = requestMessage(
            requestError, 'No se pudieron cargar los movimientos.',
          )
          if (message) setError(message)
        }).finally(() => {
          if (!controller.signal.aborted) setLoading(false)
        })
    }, 0)
    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [enabled, reloadKey])

  return { data, loading, error, reload }
}

export function useSales(filters: SaleFilters) {
  const { number, page, pageSize } = filters
  const [data, setData] = useState<SaleListResponse>(emptySales)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void listSales({ number, page, pageSize }, controller.signal)
        .then(setData).catch((requestError: unknown) => {
          const message = requestMessage(
            requestError, 'No se pudieron cargar las ventas.',
          )
          if (message) setError(message)
        }).finally(() => {
          if (!controller.signal.aborted) setLoading(false)
        })
    }, number ? 300 : 0)
    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [number, page, pageSize, reloadKey])

  return { data, loading, error, reload }
}
