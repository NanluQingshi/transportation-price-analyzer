import { chatEventSchema, type ChatEvent } from '@/types/chat'

export async function* streamChat(message: string): AsyncGenerator<ChatEvent> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })

  if (!response.ok || !response.body) {
    const text = await response.text().catch(() => 'Unknown error')
    throw new Error(`Chat request failed: ${text}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6).trim()
      if (!raw) continue
      try {
        const parsed = JSON.parse(raw) as unknown
        const event = chatEventSchema.parse(parsed)
        yield event
      } catch {
        // 忽略无法解析的 SSE 行
      }
    }
  }
}
