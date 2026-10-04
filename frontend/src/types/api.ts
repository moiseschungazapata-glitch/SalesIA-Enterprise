import type { UserRole } from '../app/navigation'

export interface AuthUser {
  id: number
  name: string
  email: string
  role: UserRole
}

export interface SessionUser extends AuthUser {
  active: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  user: AuthUser
}

export interface SecuritySession {
  id: number
  ip_address: string | null
  user_agent: string | null
  created_at: string
  expires_at: string
  last_seen_at: string
  revoked_at: string | null
  current: boolean
}

export interface SecuritySessionList {
  items: SecuritySession[]
}

export interface AccessLocation {
  id: number
  user_id: number
  user_name: string
  user_email: string
  ip_address: string | null
  user_agent: string | null
  created_at: string
  last_seen_at: string
  revoked_at: string | null
  current: boolean
  latitude: number | null
  longitude: number | null
  city: string | null
  region: string | null
  country: string | null
  country_code: string | null
  isp: string | null
  timezone: string | null
  location_source: string | null
  located_at: string | null
}

export interface AccessLocationList {
  items: AccessLocation[]
}

export interface AuditLogRecord {
  id: number
  user_id: number | null
  user_name: string | null
  action: string
  entity_type: string
  entity_id: string | null
  changes: Record<string, unknown>
  request_id: string | null
  ip_address: string | null
  created_at: string
}

export interface AuditLogList {
  items: AuditLogRecord[]
  total: number
  page: number
  page_size: number
}

export interface UserRecord extends SessionUser {
  created_at: string
  updated_at: string
}

export interface UserListResponse {
  items: UserRecord[]
  total: number
  page: number
  page_size: number
}

export interface UserCreateRequest {
  name: string
  email: string
  password: string
  role: UserRole
}

export interface UserUpdateRequest {
  name?: string
  email?: string
  role?: UserRole
  active?: boolean
  new_password?: string
}

export type CustomerType = 'person' | 'company'
export type DocumentType = 'DNI' | 'RUC'

export interface CustomerRecord {
  id: number
  customer_type: CustomerType
  document_type: DocumentType
  document_number: string
  name: string
  phone: string | null
  email: string | null
  address: string | null
  active: boolean
  created_at: string
  updated_at: string
}

export interface CustomerListResponse {
  items: CustomerRecord[]
  total: number
  page: number
  page_size: number
}

export interface CustomerCreateRequest {
  customer_type: CustomerType
  document_type: DocumentType
  document_number: string
  name: string
  phone?: string | null
  email?: string | null
  address?: string | null
}

export interface CustomerUpdateRequest {
  name?: string
  phone?: string | null
  email?: string | null
  address?: string | null
  active?: boolean
}

export interface CategoryRecord {
  id: number
  name: string
  description: string | null
  active: boolean
  created_at: string
  updated_at: string
}

export interface CategoryListResponse {
  items: CategoryRecord[]
  total: number
  page: number
  page_size: number
}

export interface CategoryCreateRequest {
  name: string
  description?: string | null
}

export interface CategoryUpdateRequest {
  name?: string
  description?: string | null
  active?: boolean
}

export interface ProductRecord {
  id: number
  sku: string
  name: string
  description: string | null
  category_id: number
  category_name: string
  unit_price: string
  stock: number
  active: boolean
  created_at: string
  updated_at: string
}

export interface ProductListResponse {
  items: ProductRecord[]
  total: number
  page: number
  page_size: number
}

export interface ProductCreateRequest {
  sku: string
  name: string
  description?: string | null
  category_id: number
  unit_price: string
  initial_stock: number
}

export interface ProductUpdateRequest {
  sku?: string
  name?: string
  description?: string | null
  category_id?: number
  unit_price?: string
  active?: boolean
}

export interface InventoryRecord {
  product_id: number
  sku: string
  product_name: string
  category_name: string
  stock: number
  active: boolean
  updated_at: string
}

export interface InventoryListResponse {
  items: InventoryRecord[]
  total: number
  page: number
  page_size: number
}

export type InventoryMovementType =
  | 'initial'
  | 'entry'
  | 'adjustment_in'
  | 'adjustment_out'
  | 'sale'

export type ManualInventoryMovementType = Exclude<
  InventoryMovementType,
  'sale'
>

export interface InventoryMovementRecord {
  id: number
  product_id: number
  sku: string
  product_name: string
  movement_type: InventoryMovementType
  quantity: number
  stock_before: number
  stock_after: number
  reason: string
  user_id: number
  user_name: string
  sale_id: number | null
  sale_number: string | null
  created_at: string
}

export interface InventoryMovementListResponse {
  items: InventoryMovementRecord[]
  total: number
  page: number
  page_size: number
}

export interface InventoryMovementCreateRequest {
  product_id: number
  movement_type: ManualInventoryMovementType
  quantity: number
  reason: string
}

export type PaymentMethod = 'cash' | 'card' | 'bank_transfer'

export interface SaleParty {
  id: number
  name: string
}

export interface SaleItemRecord {
  product_id: number
  sku: string
  product_name: string
  category_name: string
  quantity: number
  unit_price: string
  subtotal: string
}

export interface SalePaymentRecord {
  method: PaymentMethod
  amount: string
  status: 'completed'
  paid_at: string
}

export interface SaleRecord {
  id: number
  number: string
  status: 'confirmed'
  created_at: string
  customer: SaleParty
  seller: SaleParty
  items: SaleItemRecord[]
  payment: SalePaymentRecord
  currency: 'PEN'
  total: string
}

export interface SaleListItem {
  id: number
  number: string
  status: 'confirmed'
  created_at: string
  customer: SaleParty
  seller: SaleParty
  items_count: number
  payment_method: PaymentMethod
  currency: 'PEN'
  total: string
}

export interface SaleListResponse {
  items: SaleListItem[]
  total: number
  page: number
  page_size: number
}

export interface SaleCreateRequest {
  customer_id: number
  payment_method: PaymentMethod
  items: Array<{
    product_id: number
    quantity: number
  }>
}

export type StatisticalVariableType =
  | 'qualitative'
  | 'quantitative_discrete'
  | 'quantitative_continuous'

export type StatisticalAnalysisType =
  | 'mean'
  | 'median'
  | 'comparison'
  | 'frequency'
  | 'random_variable'
  | 'bayes'
  | 'insight'

export interface StatisticalVariableDefinition {
  name: string
  label: string
  variable_type: StatisticalVariableType
  data_type: 'integer' | 'decimal' | 'text' | 'boolean' | 'datetime'
  unit: string | null
  description: string
}

export interface StatisticalResultRecord {
  metric: string
  numeric_value: string | null
  text_value: string | null
  details: Record<string, unknown>
}

export interface AnalysisExecutionRecord {
  analysis_id: number
  dataset_id: number
  dataset_name: string
  analysis_type: StatisticalAnalysisType
  variable_name: string | null
  variable_label: string | null
  variable_type: StatisticalVariableType | null
  observation_count: number
  results: StatisticalResultRecord[]
  created_at: string
  completed_at: string
}

export interface AnalysisHistoryRecord extends AnalysisExecutionRecord {
  status: 'pending' | 'completed' | 'failed'
  parameters: Record<string, unknown>
}

export interface AnalysisHistoryResponse {
  items: AnalysisHistoryRecord[]
  total: number
  page: number
  page_size: number
}

export interface SalesComparisonRequest {
  metric: 'sale_total' | 'items_per_sale'
  date_from?: string | null
  date_to?: string | null
}

export interface EventProbabilityRequest {
  event_name: string
  favorable_cases: number
  total_observations: number
}

export interface RandomVariableAnalysisRequest {
  name: string
  variable_name: string
  variable_label: string
  variable_type: Extract<
    StatisticalVariableType,
    'quantitative_discrete' | 'quantitative_continuous'
  >
  random_variable_type: 'discrete' | 'continuous'
  unit?: string | null
  values: number[]
}

export interface BayesAnalysisRequest {
  event_a: string
  event_b: string
  probability_a: string
  probability_b_given_a: string
  probability_b: string
}

export type DashboardGranularity = 'day' | 'week' | 'month'

export interface DashboardKpis {
  sales_total: string
  transactions: number
  active_customers: number
  units_sold: number
  ticket_average: string
  sales_mean: string
  sales_median: string
}

export interface DashboardPeriodPoint {
  period: string
  revenue: string
  transactions: number
}

export interface DashboardBreakdownPoint {
  id: number
  label: string
  revenue: string
  transactions: number
  units: number
  share: string
}

export interface DashboardDistributionPoint {
  label: string
  frequency: number
  percentage: string
}

export interface DashboardIntegerOption {
  id: number
  label: string
}

export interface DashboardSummary {
  generated_at: string
  currency: 'PEN'
  period: {
    date_from: string
    date_to: string
    granularity: DashboardGranularity
  }
  applied_filters: {
    branch: 'main'
    seller_id: number | null
    category_id: number | null
  }
  filter_options: {
    branches: Array<{ id: 'main'; label: string }>
    sellers: DashboardIntegerOption[]
    categories: DashboardIntegerOption[]
  }
  kpis: DashboardKpis
  sales_by_period: DashboardPeriodPoint[]
  sales_by_product: DashboardBreakdownPoint[]
  sales_by_seller: DashboardBreakdownPoint[]
  ticket_distribution: DashboardDistributionPoint[]
}

export type InsightCategory =
  | 'sales'
  | 'products'
  | 'sellers'
  | 'customers'
  | 'statistics'

export type InsightSeverity = 'info' | 'warning' | 'critical'

export interface InsightRecord {
  id: number
  analysis_id: number
  dataset_id: number
  dataset_name: string
  title: string
  description: string
  category: InsightCategory
  rule_code: string
  severity: InsightSeverity
  evidence: Record<string, unknown>
  active: boolean
  period_start: string | null
  period_end: string | null
  generated_at: string
}

export interface InsightGenerationRequest {
  date_from?: string | null
  date_to?: string | null
  branch: 'main'
  seller_id?: number | null
  category_id?: number | null
}

export interface InsightGenerationResponse {
  analysis_id: number
  dataset_id: number
  generated_count: number
  items: InsightRecord[]
}

export interface InsightListResponse {
  items: InsightRecord[]
  total: number
  page: number
  page_size: number
}

export type ReportType =
  | 'sales'
  | 'products'
  | 'customers'
  | 'sellers'
  | 'statistical'

export type ReportStatus = 'pending' | 'completed' | 'failed'

export interface ReportColumn {
  key: string
  label: string
  format: 'text' | 'date' | 'datetime' | 'integer' | 'money' | 'decimal' | 'status'
}

export interface ReportContent {
  columns: ReportColumn[]
  rows: Array<Record<string, unknown>>
  summary: Record<string, unknown>
}

export interface ReportRecord {
  id: number
  report_type: ReportType
  title: string
  parameters: Record<string, unknown>
  status: ReportStatus
  row_count: number
  created_at: string
  generated_at: string | null
}

export interface ReportDetail extends ReportRecord {
  content: ReportContent
}

export interface ReportListResponse {
  items: ReportRecord[]
  total: number
  page: number
  page_size: number
}

export interface ReportGenerateRequest {
  report_type: ReportType
  title?: string | null
  date_from?: string | null
  date_to?: string | null
}
