import {
  dashboardResponseSchema,
  flightOfferSchema,
  routeSummarySchema,
  searchResponseSchema,
  trendsResponseSchema,
} from './flight'

describe('flightOfferSchema', () => {
  const validOffer = {
    flight_number: 'CA1234',
    airline: 'Air China',
    airline_code: 'CA',
    origin: 'PEK',
    destination: 'SHA',
    departure_time: '08:00',
    arrival_time: '10:15',
    duration_minutes: 135,
    price: 680.0,
    currency: 'CNY',
    cabin_class: 'ECONOMY',
    source: 'amadeus',
  }

  it('parses valid offer', () => {
    const result = flightOfferSchema.parse(validOffer)
    expect(result.flight_number).toBe('CA1234')
    expect(result.price).toBe(680.0)
  })

  it('rejects missing required field', () => {
    expect(() => flightOfferSchema.parse({ ...validOffer, flight_number: undefined })).toThrow()
  })

  it('rejects non-number price', () => {
    expect(() => flightOfferSchema.parse({ ...validOffer, price: 'free' })).toThrow()
  })
})

describe('searchResponseSchema', () => {
  it('parses valid response', () => {
    const data = {
      results: [],
      cached: false,
      query_time_ms: 1240,
    }
    const result = searchResponseSchema.parse(data)
    expect(result.cached).toBe(false)
    expect(result.results).toHaveLength(0)
  })

  it('rejects non-boolean cached', () => {
    expect(() => searchResponseSchema.parse({ results: [], cached: 'yes', query_time_ms: 0 })).toThrow()
  })
})

describe('trendsResponseSchema', () => {
  const validTrends = {
    origin: 'PEK',
    destination: 'SHA',
    days: 30,
    data_points: [
      { date: '2026-06-01', min_price: 500, avg_price: 620, max_price: 800, currency: 'CNY' },
    ],
    stats: {
      historical_min: 480,
      historical_avg: 600,
      current_price: 500,
      price_level: 'below_average',
    },
  }

  it('parses valid trends response', () => {
    const result = trendsResponseSchema.parse(validTrends)
    expect(result.origin).toBe('PEK')
    expect(result.data_points).toHaveLength(1)
    expect(result.stats.price_level).toBe('below_average')
  })

  it('parses with null current_price', () => {
    const result = trendsResponseSchema.parse({
      ...validTrends,
      stats: { ...validTrends.stats, current_price: null },
    })
    expect(result.stats.current_price).toBeNull()
  })

  it('rejects invalid price_level', () => {
    expect(() =>
      trendsResponseSchema.parse({
        ...validTrends,
        stats: { ...validTrends.stats, price_level: 'unknown_value' },
      }),
    ).toThrow()
  })
})

describe('routeSummarySchema', () => {
  const validSummary = {
    origin: 'PEK',
    destination: 'SHA',
    origin_city: '北京',
    destination_city: '上海',
    min_price: 680,
    currency: 'CNY',
    price_change: -20,
    price_change_pct: -2.9,
    trend: 'down' as const,
  }

  it('parses valid summary', () => {
    const result = routeSummarySchema.parse(validSummary)
    expect(result.trend).toBe('down')
  })

  it('rejects invalid trend value', () => {
    expect(() => routeSummarySchema.parse({ ...validSummary, trend: 'sideways' })).toThrow()
  })
})

describe('dashboardResponseSchema', () => {
  it('parses valid dashboard response', () => {
    const result = dashboardResponseSchema.parse({ date: '2026-06-19', routes: [] })
    expect(result.routes).toHaveLength(0)
    expect(result.date).toBe('2026-06-19')
  })
})
