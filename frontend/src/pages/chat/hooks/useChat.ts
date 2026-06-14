import { useCallback, useRef, useState } from 'react'
import { streamChat } from '@/services/chatApi'
import type { ChatMessage } from '@/types/chat'

let msgId = 0
const nextId = () => String(++msgId)

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const abortRef = useRef<boolean>(false)

  const sendMessage = useCallback(async (text: string) => {
    if (isStreaming) return

    // 追加用户消息
    const userMsg: ChatMessage = { id: nextId(), role: 'user', textChunks: [text], toolCalls: [] }
    // 追加 assistant 占位
    const assistantId = nextId()
    const assistantMsg: ChatMessage = { id: assistantId, role: 'assistant', textChunks: [], toolCalls: [] }
    setMessages((prev) => [...prev, userMsg, assistantMsg])

    setIsStreaming(true)
    abortRef.current = false

    try {
      for await (const event of streamChat(text)) {
        if (abortRef.current) break

        setMessages((prev) =>
          prev.map((m) => {
            if (m.id !== assistantId) return m
            switch (event.type) {
              case 'text':
                return { ...m, textChunks: [...m.textChunks, event.content] }
              case 'tool_call':
                return { ...m, toolCalls: [...m.toolCalls, { tool: event.tool, args: event.args }] }
              case 'tool_result': {
                const calls = [...m.toolCalls]
                // 找最后一个同名且尚未有结果的工具调用
                let idx = -1
                for (let j = calls.length - 1; j >= 0; j--) {
                  if (calls[j]!.tool === event.tool && calls[j]!.result === undefined) {
                    idx = j
                    break
                  }
                }
                if (idx >= 0) {
                  const prev = calls[idx]!
                  calls[idx] = { tool: prev.tool, args: prev.args, result: event.data }
                }
                return { ...m, toolCalls: calls }
              }
              default:
                return m
            }
          }),
        )
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error'
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, textChunks: [`出错了：${errMsg}`] } : m,
        ),
      )
    } finally {
      setIsStreaming(false)
    }
  }, [isStreaming])

  const stop = useCallback(() => { abortRef.current = true }, [])
  const clear = useCallback(() => { setMessages([]); msgId = 0 }, [])

  return { messages, isStreaming, sendMessage, stop, clear }
}
