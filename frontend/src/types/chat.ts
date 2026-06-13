import { z } from 'zod'

export const chatEventSchema = z.union([
  z.object({ type: z.literal('text'), content: z.string() }),
  z.object({ type: z.literal('tool_call'), tool: z.string(), args: z.record(z.string(), z.unknown()) }),
  z.object({ type: z.literal('tool_result'), tool: z.string(), data: z.unknown() }),
  z.object({ type: z.literal('done') }),
])

export type ChatEvent = z.infer<typeof chatEventSchema>

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  // text 块按顺序追加，tool_calls 记录工具调用过程
  textChunks: string[]
  toolCalls: { tool: string; args: Record<string, unknown>; result?: unknown }[]
}
