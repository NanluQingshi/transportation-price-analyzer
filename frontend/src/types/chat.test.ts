import { chatEventSchema } from './chat'

describe('chatEventSchema', () => {
  it('parses text event', () => {
    const result = chatEventSchema.parse({ type: 'text', content: '分析结果：...' })
    expect(result.type).toBe('text')
    if (result.type === 'text') {
      expect(result.content).toBe('分析结果：...')
    }
  })

  it('parses tool_call event', () => {
    const result = chatEventSchema.parse({
      type: 'tool_call',
      tool: 'search_flights',
      args: { origin: 'PEK', destination: 'SHA' },
    })
    expect(result.type).toBe('tool_call')
  })

  it('parses tool_result event', () => {
    const result = chatEventSchema.parse({
      type: 'tool_result',
      tool: 'search_flights',
      data: { offers: [] },
    })
    expect(result.type).toBe('tool_result')
  })

  it('parses done event', () => {
    const result = chatEventSchema.parse({ type: 'done' })
    expect(result.type).toBe('done')
  })

  it('rejects unknown event type', () => {
    expect(() => chatEventSchema.parse({ type: 'unknown' })).toThrow()
  })

  it('rejects text event without content', () => {
    expect(() => chatEventSchema.parse({ type: 'text' })).toThrow()
  })

  it('rejects tool_call without tool name', () => {
    expect(() =>
      chatEventSchema.parse({ type: 'tool_call', args: {} }),
    ).toThrow()
  })
})
