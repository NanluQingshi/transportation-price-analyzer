import { z } from 'zod'

export const alertResponseSchema = z.object({
  id: z.number(),
  origin: z.string(),
  destination: z.string(),
  target_price: z.number(),
  notify_channel: z.string(),
  notify_target: z.string(),
  is_active: z.boolean(),
  last_triggered_at: z.string().nullable(),
  created_at: z.string(),
})

export const alertsListResponseSchema = z.object({
  alerts: z.array(alertResponseSchema),
})

export type AlertResponse = z.infer<typeof alertResponseSchema>

export interface AlertCreate {
  origin: string
  destination: string
  target_price: number
  notify_channel: 'webhook'
  notify_target: string
}
