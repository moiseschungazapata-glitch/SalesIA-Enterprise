import { useCallback, useEffect, useState } from 'react'
import {
  listCategories,
  listProducts,
  type CategoryListFilters,
  type ProductListFilters,
} from '../services/catalog'
import type {
  CategoryListResponse,
  ProductListResponse,
} from '../types/api'

const emptyCategories: CategoryListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 100,
}

const emptyProducts: ProductListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
}

export function useCategories(filters: CategoryListFilters) {
  const { page, pageSize, search, status } = filters
  const [data, setData] = useState<CategoryListResponse>(emptyCategories)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      setLoading(true)
      setError('')
      void listCategories(
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
              : 'No se pudieron cargar las categorías.',
          )
        })
        .finally(() => {
          if (!controller.signal.aborted) {
            setLoading(false)
          }
        })
    }, 0)
    return () => {
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [page, pageSize, reloadKey, search, status])

  return { data, loading, error, reload }
}

export function useProducts(filters: ProductListFilters) {
  const { categoryId, page, pageSize, search, status } = filters
  const [data, setData] = useState<ProductListResponse>(emptyProducts)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(
      () => {
        setLoading(true)
        setError('')
        void listProducts(
          { categoryId, page, pageSize, search, status },
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
                : 'No se pudieron cargar los productos.',
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
  }, [categoryId, page, pageSize, reloadKey, search, status])

  return { data, loading, error, reload }
}
