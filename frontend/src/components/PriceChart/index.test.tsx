import { render, screen } from '@testing-library/react'
import { PriceChart } from './index'
import type { PriceDataPoint } from '@/types/flight'

const mockData: PriceDataPoint[] = [
  { date: '2026-06-01', min_price: 500, avg_price: 620, max_price: 800, currency: 'CNY' },
  { date: '2026-06-02', min_price: 480, avg_price: 600, max_price: 750, currency: 'CNY' },
]

describe('PriceChart', () => {
  it('renders empty state when no data', () => {
    render(<PriceChart data={[]} />)
    expect(screen.getByText('暂无历史数据')).toBeInTheDocument()
  })

  it('does not render empty state when data is provided', () => {
    render(<PriceChart data={mockData} />)
    // jsdom 不支持 SVG 布局，仅验证空状态不出现
    expect(screen.queryByText('暂无历史数据')).not.toBeInTheDocument()
  })
})
