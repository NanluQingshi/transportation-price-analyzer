import { apiClient } from './apiClient'
import { alertResponseSchema, alertsListResponseSchema, type AlertCreate, type AlertResponse } from '@/types/alerts'

export async function fetchAlerts(): Promise<AlertResponse[]> {
  const { data } = await apiClient.get('/alerts')
  return alertsListResponseSchema.parse(data).alerts
}

export async function createAlert(body: AlertCreate): Promise<AlertResponse> {
  const { data } = await apiClient.post('/alerts', body)
  return alertResponseSchema.parse(data)
}

export async function deleteAlert(id: number): Promise<void> {
  await apiClient.delete(`/alerts/${id}`)
}
