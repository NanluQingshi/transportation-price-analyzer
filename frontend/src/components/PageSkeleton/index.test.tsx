import { render, screen } from '@testing-library/react'
import { PageSkeleton } from './index'

describe('PageSkeleton', () => {
  it('renders without crashing', () => {
    const { container } = render(<PageSkeleton />)
    expect(container.firstChild).toBeInTheDocument()
  })

  it('has min-h-screen class for full-page layout', () => {
    const { container } = render(<PageSkeleton />)
    expect(container.querySelector('.min-h-screen')).toBeInTheDocument()
  })

  it('shows animated pulse elements', () => {
    const { container } = render(<PageSkeleton />)
    const pulses = container.querySelectorAll('.animate-pulse')
    expect(pulses.length).toBeGreaterThan(0)
  })
})
