import type {
  CategoryCreateRequest,
  CategoryListResponse,
  CategoryRecord,
  CategoryUpdateRequest,
  ProductCreateRequest,
  ProductListResponse,
  ProductRecord,
  ProductUpdateRequest,
} from '../types/api'
import { apiGet, apiPatch, apiPost } from './api'

export interface CategoryListFilters {
  page: number
  pageSize: number
  search: string
  status: 'active' | 'inactive' | ''
}

export interface ProductListFilters {
  page: number
  pageSize: number
  search: string
  categoryId: number | null
  status: 'active' | 'inactive' | ''
}

export function listCategories(
  filters: CategoryListFilters,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    page: String(filters.page),
    page_size: String(filters.pageSize),
  })
  if (filters.search.trim()) {
    query.set('search', filters.search.trim())
  }
  if (filters.status) {
    query.set('active', String(filters.status === 'active'))
  }
  return apiGet<CategoryListResponse>(`/categories?${query}`, signal)
}

export function createCategory(payload: CategoryCreateRequest) {
  return apiPost<CategoryRecord>('/categories', payload)
}

export function updateCategory(
  categoryId: number,
  payload: CategoryUpdateRequest,
) {
  return apiPatch<CategoryRecord>(`/categories/${categoryId}`, payload)
}

export function listProducts(
  filters: ProductListFilters,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    page: String(filters.page),
    page_size: String(filters.pageSize),
  })
  if (filters.search.trim()) {
    query.set('search', filters.search.trim())
  }
  if (filters.categoryId !== null) {
    query.set('category_id', String(filters.categoryId))
  }
  if (filters.status) {
    query.set('active', String(filters.status === 'active'))
  }
  return apiGet<ProductListResponse>(`/products?${query}`, signal)
}

export function createProduct(payload: ProductCreateRequest) {
  return apiPost<ProductRecord>('/products', payload)
}

export function updateProduct(
  productId: number,
  payload: ProductUpdateRequest,
) {
  return apiPatch<ProductRecord>(`/products/${productId}`, payload)
}
