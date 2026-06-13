import { apiClient } from './apiClient'
import { trendsResponseSchema, type TrendsResponse } from '@/types/flight'

export async function fetchTrends(
  origin: string,
  destination: string,
  days: 30 | 90 | 180,
): Promise<TrendsResponse> {
  const { data } = await apiClient.get('/trends', { params: { origin, destination, days } })
  return trendsResponseSchema.parse(data)
}
