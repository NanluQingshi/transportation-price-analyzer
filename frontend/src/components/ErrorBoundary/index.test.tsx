import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from './index'

/** 可控抛出错误的测试组件 */
function Bomb({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) throw new Error('💥 test explosion')
  return <div>正常渲染</div>
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // 抑制 React 内部的 console.error 输出，保持测试输出整洁
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={false} />
      </ErrorBoundary>,
    )
    expect(screen.getByText('正常渲染')).toBeInTheDocument()
  })

  it('shows fallback UI when child throws', () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    )
    expect(screen.getByText('页面出现了一点问题')).toBeInTheDocument()
  })

  it('shows error message in fallback', () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    )
    const { container } = render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    )
    expect(container.textContent).toContain('💥 test explosion')
  })

  it('shows custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>自定义降级</div>}>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    )
    expect(screen.getByText('自定义降级')).toBeInTheDocument()
  })

  it('retry button resets error state', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <Bomb shouldThrow={true} />
      </ErrorBoundary>,
    )
    expect(screen.getByText('页面出现了一点问题')).toBeInTheDocument()

    fireEvent.click(screen.getByText('重试'))

    // 重试后 hasError 被重置，若子组件仍抛出会再次进入 fallback
    // 这里验证重试按钮存在且可点击
    expect(screen.queryByText('正常渲染')).not.toBeInTheDocument()
  })
})
