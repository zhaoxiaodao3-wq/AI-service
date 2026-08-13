<template>
  <!-- 聊天页：阶段 1 接入真实对话，目前只有静态占位 -->
  <div class="chat">
    <el-empty description="聊天功能将在阶段 1 接入" />
    <div class="chat-input">
      <!-- 输入框：v-model 绑定 message，发送按钮阶段 1 前禁用 -->
      <el-input
        v-model="message"
        type="textarea"
        :rows="3"
        placeholder="输入你的问题（静态占位）"
      />
      <el-button type="primary" disabled>发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 用户输入的内容，阶段 1 在这里调用后端对话接口
const message = ref('')
</script>

<style scoped>
.chat {
  max-width: 760px;
  margin: 0 auto;
}

.chat-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
