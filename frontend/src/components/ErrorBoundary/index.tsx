import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'

export interface ErrorBoundaryProps {
  children: ReactNode
  /** 自定义降级 UI，不传则显示默认错误卡片 */
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  message: string
}

/** 捕获子树渲染错误，防止整页崩溃 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, State> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, message: '' }
  }

  static getDerivedStateFromError(error: unknown): State {
    const message = error instanceof Error ? error.message : String(error)
    return { hasError: true, message }
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  override render(): ReactNode {
    if (!this.state.hasError) return this.props.children

    if (this.props.fallback) return this.props.fallback

    return (
      <div className="flex flex-col items-center justify-center min-h-[200px] gap-3 p-8 text-center">
        <p className="text-gray-400 text-sm">页面出现了一点问题</p>
        <p className="text-xs text-gray-300 font-mono max-w-md truncate">{this.state.message}</p>
        <button
          onClick={() => this.setState({ hasError: false, message: '' })}
          className="text-sm text-blue-500 hover:underline"
        >
          重试
        </button>
      </div>
    )
  }
}
