import { z } from 'zod'

export const flightOfferSchema = z.object({
  flight_number: z.string(),
  airline: z.string(),
  airline_code: z.string(),
  origin: z.string(),
  destination: z.string(),
  departure_time: z.string(),
  arrival_time: z.string(),
  duration_minutes: z.number(),
  price: z.number(),
  currency: z.string(),
  cabin_class: z.string(),
  source: z.string(),
})

export const searchResponseSchema = z.object({
  results: z.array(flightOfferSchema),
  cached: z.boolean(),
  query_time_ms: z.number(),
})

export const airportSchema = z.object({
  iata: z.string(),
  name: z.string(),
  city: z.string(),
  country: z.string(),
})

export const airportSearchResponseSchema = z.object({
  airports: z.array(airportSchema),
})

export const routeSummarySchema = z.object({
  origin: z.string(),
  destination: z.string(),
  origin_city: z.string(),
  destination_city: z.string(),
  min_price: z.number(),
  currency: z.string(),
  price_change: z.number(),
  price_change_pct: z.number(),
  trend: z.enum(['up', 'down', 'stable']),
})

export const dashboardResponseSchema = z.object({
  date: z.string(),
  routes: z.array(routeSummarySchema),
})

export type FlightOffer = z.infer<typeof flightOfferSchema>
export type SearchResponse = z.infer<typeof searchResponseSchema>
export type Airport = z.infer<typeof airportSchema>
export type RouteSummary = z.infer<typeof routeSummarySchema>
export type DashboardResponse = z.infer<typeof dashboardResponseSchema>

export type CabinClass = 'ECONOMY' | 'BUSINESS' | 'FIRST'

export interface SearchParams {
  origin: string
  destination: string
  departure_date: string
  return_date?: string
  adults: number
  cabin_class: CabinClass
}
