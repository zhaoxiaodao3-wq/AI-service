<template>
  <!-- 豆包风格聊天页：左侧会话栏 + 居中对话流 + 底部圆角输入区 -->
  <div class="chat-page">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-logo">A</span>
        <span class="brand-text">AIGC 对话</span>
      </div>

      <button class="new-btn" @click="newSession">
        <el-icon><Plus /></el-icon>
        <span class="new-btn-text">新对话</span>
      </button>

      <div class="session-section">
        <div class="session-label">会话</div>
        <div class="session-list">
          <div
            v-for="s in sessions"
            :key="s.id"
            class="session-item"
            :class="{ active: s.id === activeSessionId }"
            :title="s.title"
            @click="switchSession(s.id)"
          >
            <span class="session-avatar">{{ s.title.slice(0, 1) }}</span>
            <span class="session-name">{{ s.title }}</span>
          </div>
        </div>
      </div>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <div class="header-left">
          <el-icon class="header-icon"><ChatDotRound /></el-icon>
          <span class="session-title">{{ activeSession?.title }}</span>
        </div>
        <el-select v-model="model" class="model-select" placeholder="选择模型">
          <el-option v-for="m in models" :key="m" :label="m" :value="m" />
        </el-select>
      </header>

      <section ref="messagesRef" class="messages">
        <div v-if="(activeSession?.messages ?? []).length === 0" class="empty-state">
          <span class="empty-logo">A</span>
          <h2>今天想聊点什么？</h2>
        </div>

        <div
          v-for="(m, i) in activeSession?.messages ?? []"
          :key="i"
          class="msg-row"
          :class="m.role"
        >
          <div v-if="m.role === 'assistant'" class="assistant-avatar">
            <el-icon><MagicStick /></el-icon>
          </div>
          <div class="msg-content">
            <div v-if="m.role === 'user' && m.attachments?.length" class="attachments">
              <template v-for="(a, ai) in m.attachments" :key="ai">
                <img
                  v-if="a.url && a.type.startsWith('image/')"
                  :src="a.url"
                  class="attachment-img"
                  alt=""
                />
                <span v-else class="attachment-chip">
                  <el-icon><Document /></el-icon>{{ a.name }}
                </span>
              </template>
            </div>
            <div v-if="m.content" class="bubble" :class="m.role">
              <span v-if="m.content.startsWith('[错误')" class="error-text">
                {{ m.content }}
              </span>
              <template v-else>
                {{ m.content }}<span
                  v-if="
                    loading &&
                    m.role === 'assistant' &&
                    activeSessionId === streamingSessionId &&
                    i === streamingIndex
                  "
                  class="caret"
                ></span>
              </template>
            </div>
          </div>
        </div>

        <div
          v-if="loading && !hasStreamedContent && activeSessionId === streamingSessionId"
          class="msg-row assistant"
        >
          <div class="assistant-avatar">
            <el-icon><MagicStick /></el-icon>
          </div>
          <div class="msg-content">
            <div class="bubble assistant typing">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </section>

      <footer class="input-area">
        <div class="input-shell">
          <div v-if="attachments.length" class="attachments">
            <span
              v-for="(a, i) in attachments"
              :key="i"
              class="attachment-chip pending"
            >
              <el-icon><Document /></el-icon>{{ a.name }}
              <el-icon class="chip-close" @click="removeAttachment(i)"><Close /></el-icon>
            </span>
          </div>
          <div class="input-row">
            <el-tooltip content="上传文件" placement="top">
              <button class="icon-btn" @click="fileInput?.click()">
                <el-icon><Paperclip /></el-icon>
              </button>
            </el-tooltip>
            <el-tooltip content="上传图片" placement="top">
              <button class="icon-btn" @click="imageInput?.click()">
                <el-icon><PictureFilled /></el-icon>
              </button>
            </el-tooltip>
            <el-input
              v-model="input"
              class="chat-input"
              type="textarea"
              :rows="1"
              :autosize="{ minRows: 1, maxRows: 5 }"
              resize="none"
              placeholder="输入你的问题，Enter 发送"
              @keydown.enter.exact.prevent="send"
            />
            <button
              class="send-btn"
              :disabled="loading || (!input.trim() && attachments.length === 0)"
              @click="send"
            >
              <el-icon><Promotion /></el-icon>
            </button>
          </div>
        </div>
        <!-- 隐藏的原生文件选择器，由上方图标按钮触发 -->
        <input
          ref="fileInput"
          type="file"
          class="hidden-input"
          @change="onFileSelected"
        />
        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          class="hidden-input"
          @change="onImageSelected"
        />
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import {
  ChatDotRound,
  Close,
  Document,
  MagicStick,
  Paperclip,
  PictureFilled,
  Plus,
  Promotion,
} from '@element-plus/icons-vue'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

import { chatStream, type ChatMessage } from '../api/chatStream'
import request from '../api/request'

interface Session {
  id: number
  title: string
  messages: ChatMessage[]
}

interface Attachment {
  name: string
  type: string
  url?: string
}

// 会话列表（内存态）：阶段 2 持久化到 PostgreSQL
const sessions = ref<Session[]>([{ id: 1, title: '新会话 1', messages: [] }])
const activeSessionId = ref(1)
// 会话自增序号，用于生成标题
let sessionSeq = 1

// 模型相关
const models = ref<string[]>([])
const model = ref('')

// 输入与附件
const input = ref('')
const attachments = ref<Attachment[]>([])
const loading = ref(false)

// 隐藏文件输入框引用
const fileInput = ref<HTMLInputElement | null>(null)
const imageInput = ref<HTMLInputElement | null>(null)
const messagesRef = ref<HTMLElement | null>(null)
const hasStreamedContent = ref(false)
const streamingSessionId = ref(-1)
const streamingIndex = ref(-1)

// 打字机缓冲区：SSE 分片先入队，定时器按节奏追加到消息内容
let pendingText = ''
let revealTimer: number | undefined
let activeAiMsg: ChatMessage | null = null

function flushTypewriter() {
  if (revealTimer !== undefined) {
    window.clearInterval(revealTimer)
    revealTimer = undefined
  }
  if (activeAiMsg && pendingText) {
    activeAiMsg.content += pendingText
    pendingText = ''
  }
}

function startReveal() {
  if (revealTimer !== undefined) return
  revealTimer = window.setInterval(() => {
    if (!activeAiMsg) return
    if (!pendingText) {
      if (revealTimer !== undefined) {
        window.clearInterval(revealTimer)
        revealTimer = undefined
      }
      return
    }
    // 每个 tick 显示一小段，形成打字机节奏
    activeAiMsg.content += pendingText.slice(0, 2)
    pendingText = pendingText.slice(2)
  }, 20)
}

// 当前激活会话
const activeSession = computed(() =>
  sessions.value.find((s) => s.id === activeSessionId.value),
)

// 创建新会话并激活，历史会话留在左侧列表
function newSession() {
  sessionSeq += 1
  const session: Session = {
    id: sessionSeq,
    title: `新会话 ${sessionSeq}`,
    messages: [],
  }
  sessions.value.push(session)
  activeSessionId.value = session.id
  input.value = ''
  attachments.value = []
}

// 切换到指定历史会话
function switchSession(id: number) {
  activeSessionId.value = id
}

// 选择普通文件：加入附件列表（不解析内容）
function onFileSelected(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  for (const file of Array.from(files)) {
    attachments.value?.push({ name: file.name, type: file.type })
  }
  ;(e.target as HTMLInputElement).value = ''
}

// 选择图片：生成本地预览 URL 后加入附件列表
function onImageSelected(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  for (const file of Array.from(files)) {
    attachments.value?.push({
      name: file.name,
      type: file.type,
      url: URL.createObjectURL(file),
    })
  }
  ;(e.target as HTMLInputElement).value = ''
}

// 移除待发送附件
function removeAttachment(index: number) {
  attachments.value?.splice(index, 1)
}

// 发送消息：组装消息 → 调 SSE → 流式渲染
async function send() {
  const session = activeSession.value
  if (!session || loading.value) return
  const content = input.value.trim()
  if (!content && attachments.value?.length === 0) return

  // 用户消息（附件随消息携带，阶段 1 后端不解析）
  const userMsg: ChatMessage = { role: 'user', content, attachments: attachments.value }
  session.messages.push(userMsg)
  input.value = ''
  attachments.value = []

  // 占位 AI 消息：push 后从数组取响应式代理，保证打字机逐字更新能被 Vue 追踪
  session.messages.push({ role: 'assistant', content: '' })
  const aiMsg = session.messages[session.messages.length - 1]
  loading.value = true
  hasStreamedContent.value = false
  streamingSessionId.value = session.id
  streamingIndex.value = session.messages.length - 1
  activeAiMsg = aiMsg
  pendingText = ''

  try {
    await chatStream(
      session.messages.map((m) => ({ role: m.role, content: m.content, attachments: m.attachments })),
      model.value,
      {
        onDelta: (delta) => {
          hasStreamedContent.value = true
          pendingText += delta
          startReveal()
        },
        onDone: () => {
          flushTypewriter()
          loading.value = false
          streamingSessionId.value = -1
          streamingIndex.value = -1
          activeAiMsg = null
        },
        onError: (code, message) => {
          flushTypewriter()
          aiMsg.content = `[错误 ${code}] ${message}`
          loading.value = false
          streamingSessionId.value = -1
          streamingIndex.value = -1
          activeAiMsg = null
        },
      },
    )
  } catch {
    // fetch 网络异常兜底
    flushTypewriter()
    aiMsg.content = '[错误] 网络异常，请稍后重试'
    loading.value = false
    streamingSessionId.value = -1
    streamingIndex.value = -1
    activeAiMsg = null
  }
}

// 消息变化或加载状态变化时滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(() => activeSession.value?.messages?.length ?? 0, scrollToBottom)
watch(loading, scrollToBottom)
watch(activeSessionId, scrollToBottom)

// 页面挂载时拉取可用模型列表，并监听窗口宽度
onMounted(async () => {
  try {
    const res: any = await request.get('/models')
    models.value = res.data.models
    model.value = res.data.default_model
  } catch {
    models.value = ['glm-4-flash']
    model.value = 'glm-4-flash'
  }
})

onUnmounted(() => {
  if (revealTimer !== undefined) {
    window.clearInterval(revealTimer)
    revealTimer = undefined
  }
  activeAiMsg = null
})
</script>

<style scoped>
.chat-page {
  height: 100%;
  display: flex;
  overflow: hidden;
  background: #f5f6f7;
}

.sidebar {
  width: 240px;
  flex: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 12px;
  background: #fff;
  border-right: 1px solid #e5e6eb;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 4px;
}

.brand-logo {
  width: 34px;
  height: 34px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #4e6ef2, #7b5cff);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
}

.brand-text {
  font-size: 16px;
  font-weight: 600;
  color: #1f2329;
  white-space: nowrap;
}

.new-btn {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 8px;
  background: #4e6ef2;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.new-btn:hover {
  background: #3b5ce8;
}

.session-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.session-label {
  margin: 4px 8px 8px;
  font-size: 12px;
  color: #86909c;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 2px;
  padding: 9px 10px;
  border-radius: 8px;
  color: #1f2329;
  cursor: pointer;
  transition: background 0.15s ease;
}

.session-item:hover {
  background: #f2f3f5;
}

.session-item.active {
  background: #eef3ff;
  color: #4e6ef2;
}

.session-avatar {
  width: 26px;
  height: 26px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #e8ecf2;
  color: #4e6ef2;
  font-size: 12px;
  font-weight: 600;
}

.session-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.chat-header {
  height: 56px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.header-icon {
  color: #4e6ef2;
  font-size: 18px;
}

.session-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 16px;
  font-weight: 600;
  color: #1f2329;
}

.model-select {
  width: 220px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.empty-logo {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #4e6ef2, #7b5cff);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
}

.empty-state h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2329;
}

.msg-row {
  display: flex;
  gap: 12px;
  max-width: 760px;
  margin: 0 auto 20px;
}

.msg-row.user {
  justify-content: flex-end;
}

.assistant-avatar {
  width: 32px;
  height: 32px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #4e6ef2, #7b5cff);
  color: #fff;
  font-size: 16px;
}

.msg-content {
  max-width: 72%;
  min-width: 0;
}

.msg-row.user .msg-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.bubble {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 15px;
  line-height: 1.65;
  color: #1f2329;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble.user {
  background: #eef3ff;
  border-top-right-radius: 4px;
}

.bubble.assistant {
  background: #fff;
  border: 1px solid #eef0f3;
  border-top-left-radius: 4px;
}

.error-text {
  color: #e5484d;
}

.typing {
  display: flex;
  align-items: center;
  gap: 5px;
  min-height: 24px;
}

.caret {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 2px;
  vertical-align: text-bottom;
  background: #4e6ef2;
  animation: caret-blink 1s steps(2, start) infinite;
}

@keyframes caret-blink {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c2c8d1;
  animation: breathe 1.2s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes breathe {
  0%,
  60%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.attachment-img {
  width: 96px;
  height: 96px;
  object-fit: cover;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 200px;
  padding: 6px 10px;
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  font-size: 13px;
  color: #4e5969;
}

.attachment-chip .el-icon {
  color: #4e6ef2;
}

.chip-close {
  cursor: pointer;
  color: #86909c;
}

.input-area {
  flex: none;
  display: flex;
  justify-content: center;
  padding: 12px 24px 20px;
}

.input-shell {
  width: 100%;
  max-width: 760px;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(31, 35, 41, 0.06);
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 6px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #4e5969;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.icon-btn:hover {
  background: #f2f3f5;
  color: #4e6ef2;
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  padding: 8px 4px;
  border: none;
  background: transparent;
  box-shadow: none;
  font-size: 15px;
}

.send-btn {
  width: 36px;
  height: 36px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 10px;
  background: #4e6ef2;
  color: #fff;
  font-size: 17px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.send-btn:hover:not(:disabled) {
  background: #3b5ce8;
}

.send-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.hidden-input {
  display: none;
}

@media (max-width: 768px) {
  .sidebar {
    width: 64px;
    align-items: center;
    padding: 16px 8px;
  }

  .brand {
    justify-content: center;
    padding: 0;
  }

  .brand-text,
  .new-btn-text,
  .session-label,
  .session-name {
    display: none;
  }

  .new-btn {
    padding: 0;
  }

  .session-item {
    justify-content: center;
    padding: 8px;
  }

  .chat-header {
    padding: 0 12px;
  }

  .model-select {
    width: 150px;
  }

  .messages {
    padding: 16px 10px;
  }

  .msg-content {
    max-width: 85%;
  }

  .input-area {
    padding: 10px 10px 14px;
  }
}
</style>
