import { routeResponseSchema, routesListResponseSchema } from './routes'

describe('routeResponseSchema', () => {
  const validRoute = {
    id: 1,
    origin: 'PEK',
    destination: 'SHA',
    is_active: true,
    created_at: '2026-06-01T00:00:00Z',
  }

  it('parses valid route', () => {
    const result = routeResponseSchema.parse(validRoute)
    expect(result.id).toBe(1)
    expect(result.is_active).toBe(true)
  })

  it('parses inactive route', () => {
    const result = routeResponseSchema.parse({ ...validRoute, is_active: false })
    expect(result.is_active).toBe(false)
  })

  it('rejects missing id', () => {
    expect(() => routeResponseSchema.parse({ ...validRoute, id: undefined })).toThrow()
  })

  it('rejects non-boolean is_active', () => {
    expect(() => routeResponseSchema.parse({ ...validRoute, is_active: 'yes' })).toThrow()
  })
})

describe('routesListResponseSchema', () => {
  it('parses empty routes list', () => {
    const result = routesListResponseSchema.parse({ routes: [] })
    expect(result.routes).toHaveLength(0)
  })

  it('parses multiple routes', () => {
    const result = routesListResponseSchema.parse({
      routes: [
        { id: 1, origin: 'PEK', destination: 'SHA', is_active: true, created_at: '2026-06-01T00:00:00Z' },
        { id: 2, origin: 'SHA', destination: 'CAN', is_active: false, created_at: '2026-06-02T00:00:00Z' },
      ],
    })
    expect(result.routes).toHaveLength(2)
    expect(result.routes[0]?.origin).toBe('PEK')
  })
})
