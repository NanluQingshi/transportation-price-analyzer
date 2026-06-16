import { render, screen } from '@testing-library/react'
import { FlightCard } from './index'
import type { FlightOffer } from '@/types/flight'

const mockOffer: FlightOffer = {
  flight_number: 'CA1234',
  airline: 'Air China',
  airline_code: 'CA',
  origin: 'PEK',
  destination: 'SHA',
  departure_time: '08:00',
  arrival_time: '10:15',
  duration_minutes: 135,
  price: 680,
  currency: 'CNY',
  cabin_class: 'ECONOMY',
  source: 'amadeus',
}

describe('FlightCard', () => {
  it('renders flight number', () => {
    render(<FlightCard offer={mockOffer} />)
    expect(screen.getByText('CA1234')).toBeInTheDocument()
  })

  it('renders origin and destination codes', () => {
    render(<FlightCard offer={mockOffer} />)
    expect(screen.getByText('PEK')).toBeInTheDocument()
    expect(screen.getByText('SHA')).toBeInTheDocument()
  })

  it('renders formatted price', () => {
    render(<FlightCard offer={mockOffer} />)
    expect(screen.getByText('¥680')).toBeInTheDocument()
  })

  it('renders departure and arrival times', () => {
    render(<FlightCard offer={mockOffer} />)
    expect(screen.getByText('08:00')).toBeInTheDocument()
    expect(screen.getByText('10:15')).toBeInTheDocument()
  })

  it('renders duration in hours and minutes', () => {
    const { container } = render(<FlightCard offer={mockOffer} />)
    expect(container.textContent).toContain('2h 15m')
  })

  it('renders duration in minutes only when less than an hour', () => {
    const { container } = render(<FlightCard offer={{ ...mockOffer, duration_minutes: 45 }} />)
    expect(container.textContent).toContain('45m')
  })
})
