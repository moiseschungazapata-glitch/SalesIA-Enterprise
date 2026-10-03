import type {
  AnalysisExecutionRecord,
  AnalysisHistoryResponse,
  BayesAnalysisRequest,
  EventProbabilityRequest,
  RandomVariableAnalysisRequest,
  SalesComparisonRequest,
  StatisticalVariableDefinition,
} from '../types/api'
import { apiGet, apiPost } from './api'

export function listStatisticalVariables(signal?: AbortSignal) {
  return apiGet<StatisticalVariableDefinition[]>(
    '/statistics/variables',
    signal,
  )
}

export function listAnalysisHistory(signal?: AbortSignal) {
  return apiGet<AnalysisHistoryResponse>(
    '/statistics/analyses?page=1&page_size=50',
    signal,
  )
}

export function compareSalesStatistics(payload: SalesComparisonRequest) {
  return apiPost<AnalysisExecutionRecord>(
    '/statistics/sales/compare',
    payload,
  )
}

export function calculateEventProbability(
  payload: EventProbabilityRequest,
) {
  return apiPost<AnalysisExecutionRecord>(
    '/probability/events',
    payload,
  )
}

export function analyzeRandomVariable(
  payload: RandomVariableAnalysisRequest,
) {
  return apiPost<AnalysisExecutionRecord>(
    '/random-variables/analyze',
    payload,
  )
}

export function calculateBayes(payload: BayesAnalysisRequest) {
  return apiPost<AnalysisExecutionRecord>('/probability/bayes', payload)
}
