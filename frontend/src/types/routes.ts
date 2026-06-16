import { z } from 'zod'

export const routeResponseSchema = z.object({
  id: z.number(),
  origin: z.string(),
  destination: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
})

export const routesListResponseSchema = z.object({
  routes: z.array(routeResponseSchema),
})

export type RouteResponse = z.infer<typeof routeResponseSchema>
