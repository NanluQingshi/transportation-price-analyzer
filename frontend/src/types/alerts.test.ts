import { alertResponseSchema, alertsListResponseSchema } from './alerts'

describe('alertResponseSchema', () => {
  const validAlert = {
    id: 1,
    origin: 'PEK',
    destination: 'SHA',
    target_price: 500.0,
    notify_channel: 'webhook',
    notify_target: 'https://example.com/hook',
    is_active: true,
    last_triggered_at: null,
    created_at: '2026-06-01T00:00:00Z',
  }

  it('parses valid alert', () => {
    const result = alertResponseSchema.parse(validAlert)
    expect(result.id).toBe(1)
    expect(result.target_price).toBe(500.0)
    expect(result.last_triggered_at).toBeNull()
  })

  it('parses alert with last_triggered_at', () => {
    const result = alertResponseSchema.parse({
      ...validAlert,
      last_triggered_at: '2026-06-15T10:00:00Z',
    })
    expect(result.last_triggered_at).toBe('2026-06-15T10:00:00Z')
  })

  it('parses inactive alert', () => {
    const result = alertResponseSchema.parse({ ...validAlert, is_active: false })
    expect(result.is_active).toBe(false)
  })

  it('rejects missing target_price', () => {
    expect(() => alertResponseSchema.parse({ ...validAlert, target_price: undefined })).toThrow()
  })
})

describe('alertsListResponseSchema', () => {
  it('parses empty alerts list', () => {
    const result = alertsListResponseSchema.parse({ alerts: [] })
    expect(result.alerts).toHaveLength(0)
  })

  it('parses list with alerts', () => {
    const data = {
      alerts: [
        {
          id: 1, origin: 'PEK', destination: 'SHA',
          target_price: 500, notify_channel: 'webhook',
          notify_target: 'https://example.com', is_active: true,
          last_triggered_at: null, created_at: '2026-06-01T00:00:00Z',
        },
      ],
    }
    const result = alertsListResponseSchema.parse(data)
    expect(result.alerts).toHaveLength(1)
  })
})
