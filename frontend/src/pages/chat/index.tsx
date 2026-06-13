import { useEffect, useRef, useState } from 'react'
import { Layout } from '@/components/Layout'
import { ToolCallBadge } from './components/ToolCallBadge'
import { useChat } from './hooks/useChat'
import type { ChatMessage } from '@/types/chat'

const EXAMPLE_PROMPTS = [
  '下个月北京到上海，什么时候最便宜？',
  '现在买北京到广州的机票合适吗？',
  '帮我对比一下北京到成都最近的价格走势',
]

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const text = msg.textChunks.join('')
  const isUser = msg.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        {!isUser && <ToolCallBadge toolCalls={msg.toolCalls} />}
        {(text || isUser) && (
          <div
            className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${
              isUser
                ? 'bg-blue-600 text-white rounded-tr-sm'
                : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'
            }`}
          >
            {text || (
              <span className="inline-flex gap-1 text-gray-400">
                <span className="animate-bounce">·</span>
                <span className="animate-bounce [animation-delay:0.1s]">·</span>
                <span className="animate-bounce [animation-delay:0.2s]">·</span>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const [input, setInput] = useState('')
  const { messages, isStreaming, sendMessage, stop, clear } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isStreaming) return
    setInput('')
    void sendMessage(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100vh-8rem)]">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">智能分析</h1>
          {messages.length > 0 && (
            <button
              onClick={clear}
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              清空对话
            </button>
          )}
        </div>

        {/* 消息区 */}
        <div className="flex-1 overflow-y-auto flex flex-col gap-4 pb-4">
          {messages.length === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center gap-6 text-center">
              <div>
                <p className="text-lg font-medium text-gray-700 mb-1">机票价格分析助手</p>
                <p className="text-sm text-gray-400">告诉我你想了解哪条航线，我来帮你分析</p>
              </div>
              <div className="flex flex-col gap-2 w-full max-w-md">
                {EXAMPLE_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => { setInput(prompt); inputRef.current?.focus() }}
                    className="text-sm text-left px-4 py-2.5 bg-white border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-colors text-gray-600"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        {/* 输入区 */}
        <div className="bg-white border border-gray-200 rounded-2xl p-3 flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入问题，例如：下个月北京到上海最便宜的是哪天？"
            rows={1}
            className="flex-1 resize-none text-sm outline-none text-gray-800 placeholder-gray-400 max-h-32 leading-relaxed"
            style={{ height: 'auto' }}
            onInput={(e) => {
              const el = e.currentTarget
              el.style.height = 'auto'
              el.style.height = `${el.scrollHeight}px`
            }}
          />
          <button
            onClick={isStreaming ? stop : handleSend}
            disabled={!isStreaming && !input.trim()}
            className={`shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              isStreaming
                ? 'bg-red-50 text-red-600 hover:bg-red-100'
                : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed'
            }`}
          >
            {isStreaming ? '停止' : '发送'}
          </button>
        </div>
      </div>
    </Layout>
  )
}
