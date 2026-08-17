<template>
  <!-- 文档上传页：PDF/TXT/MD 上传、解析、向量化入库与文档管理 -->
  <div class="upload">
    <div class="upload-panel">
      <div
        class="upload-box"
        @click="fileInput?.click()"
        @dragover.prevent
        @drop.prevent="onDrop"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <p>点击选择或拖拽 PDF / TXT / MD 文件</p>
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.txt,.md"
          class="hidden-input"
          @change="onFileSelected"
        />
      </div>

      <div v-if="uploading" class="uploading">正在解析并向量化，请稍候…</div>

      <div class="doc-list">
        <div v-for="doc in documents" :key="doc.id" class="doc-item">
          <el-icon class="doc-icon"><Document /></el-icon>
          <div class="doc-info">
            <div class="doc-name">{{ doc.filename }}</div>
            <div class="doc-meta">{{ doc.chunk_count }} 个切片 · {{ formatSize(doc.file_size) }}</div>
          </div>
          <el-icon class="doc-delete" title="删除" @click="removeDocument(doc)">
            <Delete />
          </el-icon>
        </div>
        <el-empty
          v-if="!documents.length && !uploading"
          description="还没有上传文档"
          :image-size="80"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Delete, Document, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'

import request from '../api/request'

interface Doc {
  id: number
  filename: string
  file_size: number
  chunk_count: number
  created_at: string
}

const fileInput = ref<HTMLInputElement | null>(null)
const documents = ref<Doc[]>([])
const uploading = ref(false)

async function loadDocuments() {
  try {
    const res: any = await request.get('/documents')
    documents.value = res.data.documents
  } catch {
    documents.value = []
  }
}

function onFileSelected(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files?.length) uploadFile(files[0])
  ;(e.target as HTMLInputElement).value = ''
}

function onDrop(e: DragEvent) {
  const files = e.dataTransfer?.files
  if (files?.length) uploadFile(files[0])
}

async function uploadFile(file: File) {
  if (!/\.(pdf|txt|md)$/i.test(file.name)) {
    ElMessage.error('仅支持 PDF / TXT / MD 文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    await request.post('/documents', formData, { timeout: 120000 })
    ElMessage.success('上传成功，已向量化入库')
    await loadDocuments()
  } catch {
    // 请求拦截器已提示错误
  } finally {
    uploading.value = false
  }
}

async function removeDocument(doc: Doc) {
  try {
    await ElMessageBox.confirm(`删除文档「${doc.filename}」？`, '删除确认', {
      type: 'warning',
    })
  } catch {
    return
  }
  await request.delete(`/documents/${doc.id}`)
  documents.value = documents.value.filter((d) => d.id !== doc.id)
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

onMounted(loadDocuments)
</script>

<style scoped>
.upload {
  min-height: 100%;
  display: flex;
  justify-content: center;
  padding: 24px;
}

.upload-panel {
  width: min(720px, 100%);
}

.upload-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  min-height: 200px;
  background: #fff;
  border: 1px dashed #c9cdd4;
  border-radius: 8px;
  color: #86909c;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.upload-box:hover {
  border-color: #4e6ef2;
  background: #fafbff;
}

.upload-icon {
  font-size: 44px;
  color: #4e6ef2;
}

.upload-box p {
  margin: 0;
  font-size: 14px;
}

.uploading {
  margin-top: 12px;
  padding: 10px 14px;
  background: #eef3ff;
  border-radius: 8px;
  color: #4e6ef2;
  font-size: 13px;
}

.doc-list {
  margin-top: 16px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
}

.doc-icon {
  font-size: 22px;
  color: #4e6ef2;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 600;
  color: #1f2329;
}

.doc-meta {
  margin-top: 2px;
  font-size: 12px;
  color: #86909c;
}

.doc-delete {
  padding: 6px;
  border-radius: 6px;
  color: #86909c;
  font-size: 16px;
  cursor: pointer;
}

.doc-delete:hover {
  color: #e5484d;
  background: #fef0f0;
}

.hidden-input {
  display: none;
}
</style>
<style scoped>
/* 二次元卡通覆盖层 */
.upload-box {
  background: rgba(255, 255, 255, 0.92);
  border: var(--border-w) dashed var(--color-secondary);
  border-radius: 20px;
  box-shadow: var(--shadow-outer);
}

.upload-icon {
  color: var(--color-primary);
}

.uploading {
  background: #ffe4e6;
  border: 2px solid var(--color-border);
  color: var(--color-primary);
}

.doc-item {
  border: var(--border-w) solid var(--color-border);
  border-radius: 16px;
  box-shadow: var(--shadow-outer);
}

.doc-icon {
  color: var(--color-primary);
}

.doc-delete:hover {
  color: var(--color-destructive, #dc2626);
  background: #fee2e2;
}
</style>
