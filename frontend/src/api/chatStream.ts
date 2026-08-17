// 流式对话工具：用 fetch 读取 SSE 事件。
// 为什么不用 EventSource：EventSource 只支持 GET，而对话接口是 POST，需要传消息体。

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  // 附件：阶段 1 只展示与随消息携带，不解析
  attachments?: { name: string; type: string; url?: string }[]
}

export async function chatStream(
  messages: ChatMessage[],
  model: string,
  handlers: {
    onDelta: (content: string) => void
    onDone: () => void
    onError: (code: string, message: string) => void
  },
  sessionId?: number,
  useRag = false,
) {
  const payload: {
    messages: ChatMessage[]
    model: string
    session_id?: number
    use_rag?: boolean
  } = {
    messages,
    model,
  }
  if (sessionId && sessionId > 0) {
    payload.session_id = sessionId
  }
  if (useRag) {
    payload.use_rag = true
  }
  // 发送 POST 请求，后端以 text/event-stream 持续返回
  const resp = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!resp.ok || !resp.body) {
    handlers.onError('http', `请求失败（${resp.status}）`)
    return
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  // 循环读取流式分块，SSE 事件以空行分隔，需要保留缓冲处理跨块数据
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? '' // 最后一段可能不完整，留到下一轮
    for (const part of parts) {
      const line = part.split('\n').find((l) => l.startsWith('data: '))
      if (!line) continue
      const event = JSON.parse(line.slice(6))
      if (event.type === 'delta') handlers.onDelta(event.content)
      else if (event.type === 'done') handlers.onDone()
      else if (event.type === 'error') handlers.onError(event.code, event.message)
    }
  }
}
