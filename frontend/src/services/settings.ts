import type { CommercialSettings } from '../types/api'
import { apiGet, apiPatch } from './api'

export const getCommercialSettings = (signal?: AbortSignal) =>
  apiGet<CommercialSettings>('/commercial-settings', signal)

export const updateCommercialSettings = (payload: CommercialSettings) =>
  apiPatch<CommercialSettings>('/commercial-settings', payload)
