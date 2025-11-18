import axios from 'axios'

import type { DebtItem, StarMapData } from '../types/analyzer'

const http = axios.create({
  baseURL: '/',
  timeout: 15_000,
})

export interface DebtListFilters {
  sourceType?: string
  module?: string
  difficulty?: string
}

export async function fetchStarMap(reportPath?: string): Promise<StarMapData> {
  const response = await http.get('/api/debt/star-map', {
    params: reportPath ? { report_path: reportPath } : undefined,
  })
  return response.data
}

export async function fetchDebtList(filters: DebtListFilters = {}, reportPath?: string): Promise<DebtItem[]> {
  const params: Record<string, string | undefined> = {
    report_path: reportPath,
  }

  if (filters.sourceType) {
    params.source_type = filters.sourceType
  }
  if (filters.module) {
    params.module = filters.module
  }
  if (filters.difficulty) {
    params.difficulty = filters.difficulty
  }

  const response = await http.get('/api/debt/list', {
    params,
  })
  return response.data
}
