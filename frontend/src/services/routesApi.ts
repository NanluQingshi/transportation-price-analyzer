import { apiClient } from './apiClient'
import { routeResponseSchema, routesListResponseSchema, type RouteResponse } from '@/types/routes'

export async function fetchRoutes(): Promise<RouteResponse[]> {
  const { data } = await apiClient.get('/routes')
  return routesListResponseSchema.parse(data).routes
}

export async function createRoute(origin: string, destination: string): Promise<RouteResponse> {
  const { data } = await apiClient.post('/routes', { origin, destination })
  return routeResponseSchema.parse(data)
}

export async function deleteRoute(id: number): Promise<void> {
  await apiClient.delete(`/routes/${id}`)
}
