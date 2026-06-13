import type { ChatMessage } from '@/types/chat'

export interface ToolCallBadgeProps {
  toolCalls: ChatMessage['toolCalls']
}

const TOOL_LABELS: Record<string, string> = {
  search_flights: '搜索航班',
  get_price_trend: '查询趋势',
  analyze_price: '分析价格',
}

/** 显示 Agent 调用工具的过程标签 */
export function ToolCallBadge({ toolCalls }: ToolCallBadgeProps) {
  if (toolCalls.length === 0) return null
  return (
    <div className="flex flex-wrap gap-2 mb-2">
      {toolCalls.map((call, i) => (
        <span
          key={i}
          className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${
            call.result !== undefined
              ? 'bg-blue-50 border-blue-200 text-blue-700'
              : 'bg-gray-50 border-gray-200 text-gray-500'
          }`}
        >
          {call.result !== undefined ? '✓' : '⋯'}
          {TOOL_LABELS[call.tool] ?? call.tool}
        </span>
      ))}
    </div>
  )
}
