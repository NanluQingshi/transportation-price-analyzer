import { render, screen } from '@testing-library/react'
import { ToolCallBadge } from './ToolCallBadge'

describe('ToolCallBadge', () => {
  it('renders nothing when toolCalls is empty', () => {
    const { container } = render(<ToolCallBadge toolCalls={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders pending badge without result', () => {
    const { container } = render(
      <ToolCallBadge toolCalls={[{ tool: 'search_flights', args: {} }]} />,
    )
    expect(container.textContent).toContain('搜索航班')
    expect(container.textContent).toContain('⋯')
  })

  it('renders completed badge with result', () => {
    const { container } = render(
      <ToolCallBadge
        toolCalls={[{ tool: 'get_price_trend', args: {}, result: { data: [] } }]}
      />,
    )
    expect(container.textContent).toContain('查询趋势')
    expect(container.textContent).toContain('✓')
  })

  it('renders multiple tool calls', () => {
    const { container } = render(
      <ToolCallBadge
        toolCalls={[
          { tool: 'search_flights', args: {}, result: {} },
          { tool: 'analyze_price', args: {} },
        ]}
      />,
    )
    expect(container.textContent).toContain('搜索航班')
    expect(container.textContent).toContain('分析价格')
  })

  it('renders unknown tool name as-is', () => {
    const { container } = render(
      <ToolCallBadge toolCalls={[{ tool: 'custom_tool', args: {} }]} />,
    )
    expect(container.textContent).toContain('custom_tool')
  })
})
