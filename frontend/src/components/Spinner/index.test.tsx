import { render, screen } from '@testing-library/react'
import { Spinner } from './index'

describe('Spinner', () => {
  it('renders with aria-label', () => {
    render(<Spinner />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByLabelText('加载中')).toBeInTheDocument()
  })

  it('applies default md size class', () => {
    const { container } = render(<Spinner />)
    expect(container.firstChild).toHaveClass('h-6', 'w-6')
  })

  it('applies sm size class', () => {
    const { container } = render(<Spinner size="sm" />)
    expect(container.firstChild).toHaveClass('h-4', 'w-4')
  })

  it('applies lg size class', () => {
    const { container } = render(<Spinner size="lg" />)
    expect(container.firstChild).toHaveClass('h-10', 'w-10')
  })

  it('passes additional className', () => {
    const { container } = render(<Spinner className="text-red-500" />)
    expect(container.firstChild).toHaveClass('text-red-500')
  })
})
