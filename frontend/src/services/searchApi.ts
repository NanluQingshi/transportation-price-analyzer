import { apiClient } from './apiClient'
import {
  airportSearchResponseSchema,
  dashboardResponseSchema,
  searchResponseSchema,
  type DashboardResponse,
  type SearchParams,
  type SearchResponse,
} from '@/types/flight'

export async function searchFlights(params: SearchParams): Promise<SearchResponse> {
  const { data } = await apiClient.post('/search', params)
  return searchResponseSchema.parse(data)
}

export async function searchAirports(q: string): Promise<{ iata: string; name: string; city: string; country: string }[]> {
  const { data } = await apiClient.get('/airports', { params: { q } })
  return airportSearchResponseSchema.parse(data).airports
}

export async function fetchDashboard(): Promise<DashboardResponse> {
  const { data } = await apiClient.get('/dashboard')
  return dashboardResponseSchema.parse(data)
}
