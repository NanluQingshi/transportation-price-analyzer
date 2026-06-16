export interface SpinnerProps {
  /** 尺寸，默认 md */
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const SIZE = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' }

/** 通用加载转圈 */
export function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  return (
    <div
      className={`${SIZE[size]} animate-spin rounded-full border-2 border-gray-200 border-t-blue-500 ${className}`}
      role="status"
      aria-label="加载中"
    />
  )
}
