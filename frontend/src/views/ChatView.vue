<template>
  <!-- 豆包风格布局：左侧会话菜单 + 右侧聊天区 -->
  <el-container class="chat-page">
    <!-- 左侧：新会话按钮 + 历史会话列表 -->
    <el-aside width="240px" class="sidebar">
      <div class="sidebar-title">会话</div>
      <el-button type="primary" class="new-btn" @click="newSession">
        <el-icon><Plus /></el-icon>
        新会话
      </el-button>
      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === activeSessionId }"
          @click="switchSession(s.id)"
        >
          {{ s.title }}
        </div>
      </div>
    </el-aside>

    <!-- 右侧：聊天区 -->
    <el-container class="chat-main">
      <el-header class="chat-header">
        <span class="session-title">{{ activeSession?.title }}</span>
        <!-- 模型下拉：切换后作为请求参数发送 -->
        <el-select v-model="model" placeholder="选择模型" style="width: 220px">
          <el-option v-for="m in models" :key="m" :label="m" :value="m" />
        </el-select>
      </el-header>

      <el-main class="messages">
        <div v-for="(m, i) in activeSession?.messages ?? []" :key="i" class="msg-row" :class="m.role">
          <div class="bubble">
            <!-- 附件：图片显示缩略图，其他文件显示文件名 -->
            <div v-for="a in m.attachments" :key="a.name" class="attachment">
              <img v-if="a.url && a.type.startsWith('image/')" :src="a.url" class="attachment-img" alt="" />
              <el-tag v-else>{{ a.name }}</el-tag>
            </div>
            <div class="text">{{ m.content }}</div>
          </div>
        </div>
        <!-- AI 生成中的占位提示 -->
        <div v-if="loading" class="msg-row assistant">
          <div class="bubble typing">正在思考…</div>
        </div>
      </el-main>

      <el-footer class="input-area">
        <!-- 待发送附件条 -->
        <div v-if="attachments.length" class="attachments">
          <el-tag
            v-for="(a, i) in attachments"
            :key="i"
            closable
            @close="removeAttachment(i)"
          >
            {{ a.name }}
          </el-tag>
        </div>
        <div class="input-row">
          <!-- 上传文件 / 上传图片按钮 -->
          <el-button circle title="上传文件" @click="fileInput?.click()">
            <el-icon><Paperclip /></el-icon>
          </el-button>
          <el-button circle title="上传图片" @click="imageInput?.click()">
            <el-icon><PictureFilled /></el-icon>
          </el-button>
          <el-input
            v-model="input"
            type="textarea"
            :rows="2"
            resize="none"
            placeholder="输入你的问题，Enter 发送"
            @keydown.enter.exact.prevent="send"
          />
          <el-button
            type="primary"
            :disabled="loading || (!input.trim() && attachments.length === 0)"
            @click="send"
          >
            发送
          </el-button>
        </div>
        <!-- 隐藏的原生文件选择器，由上方按钮触发 -->
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
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Paperclip, PictureFilled, Plus } from '@element-plus/icons-vue'

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

  // 占位 AI 消息，delta 增量不断追加到这里
  const aiMsg: ChatMessage = { role: 'assistant', content: '' }
  session.messages.push(aiMsg)
  loading.value = true

  try {
    await chatStream(
      session.messages.map((m) => ({ role: m.role, content: m.content, attachments: m.attachments })),
      model.value,
      {
        onDelta: (delta) => {
          aiMsg.content += delta
        },
        onDone: () => {
          loading.value = false
        },
        onError: (code, message) => {
          aiMsg.content = `[错误 ${code}] ${message}`
          loading.value = false
        },
      },
    )
  } catch {
    // fetch 网络异常兜底
    aiMsg.content = '[错误] 网络异常，请稍后重试'
    loading.value = false
  }
}

// 页面挂载时拉取可用模型列表
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
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 61px);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
}

.sidebar {
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-fill-color-light);
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.sidebar-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.new-btn {
  width: 100%;
  margin-bottom: 12px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
}

.session-item:hover {
  background: var(--el-fill-color);
}

.session-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.chat-main {
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color-light);
}

.session-title {
  font-weight: 600;
}

.messages {
  flex: 1;
  overflow-y: auto;
  background: #fff;
}

.msg-row {
  display: flex;
  margin-bottom: 16px;
}

.msg-row.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.msg-row.user .bubble {
  background: var(--el-color-primary-light-8);
}

.typing {
  color: var(--el-text-color-secondary);
}

.attachment-img {
  max-width: 160px;
  max-height: 120px;
  border-radius: 6px;
  margin-bottom: 6px;
}

.attachment {
  margin-bottom: 6px;
}

.input-area {
  border-top: 1px solid var(--el-border-color-light);
  padding: 12px;
}

.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.hidden-input {
  display: none;
}
</style>
