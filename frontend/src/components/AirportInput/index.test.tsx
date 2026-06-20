import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AirportInput } from './index'

vi.mock('@/services/searchApi', () => ({
  searchAirports: vi.fn().mockResolvedValue([
    { iata: 'PEK', name: '北京首都国际机场', city: '北京', country: '中国' },
    { iata: 'PKX', name: '北京大兴国际机场', city: '北京', country: '中国' },
  ]),
}))

function renderAirportInput(onChange = vi.fn()) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <AirportInput label="出发地" value="" onChange={onChange} placeholder="输入城市" />
    </QueryClientProvider>,
  )
}

describe('AirportInput', () => {
  it('renders label', () => {
    renderAirportInput()
    expect(screen.getByText('出发地')).toBeInTheDocument()
  })

  it('renders placeholder', () => {
    renderAirportInput()
    expect(screen.getByPlaceholderText('输入城市')).toBeInTheDocument()
  })

  it('renders input element', () => {
    renderAirportInput()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('updates input value when user types', async () => {
    const user = userEvent.setup()
    renderAirportInput()
    const input = screen.getByRole('textbox')
    await user.type(input, '北京')
    expect(input).toHaveValue('北京')
  })
})
