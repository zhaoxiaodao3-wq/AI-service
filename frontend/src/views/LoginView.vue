<template>
  <div class="login-page">
    <div class="login-card">
      <span class="login-logo">A</span>
      <h1>AIGC 对话平台</h1>
      <div class="mode-tabs">
        <button
          class="mode-tab"
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'"
        >
          登录
        </button>
        <button
          class="mode-tab"
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'"
        >
          注册
        </button>
      </div>
      <el-input
        v-model="username"
        class="field"
        placeholder="用户名"
        aria-label="用户名"
      />
      <el-input
        v-model="password"
        class="field"
        type="password"
        placeholder="密码"
        aria-label="密码"
        show-password
        @keydown.enter="submit"
      />
      <el-button
        type="primary"
        size="large"
        class="submit-btn"
        :loading="loading"
        @click="submit"
      >
        {{ mode === 'login' ? '登录' : '注册并登录' }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import request from '../api/request'

const router = useRouter()
const mode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value.trim() || !password.value) return
  loading.value = true
  try {
    const res: any = await request.post(`/auth/${mode.value}`, {
      username: username.value.trim(),
      password: password.value,
    })
    const tokens = res.data.tokens
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    localStorage.setItem('username', tokens.user.username)
    router.push('/chat')
  } catch {
    // 拦截器已提示错误
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.login-card {
  width: min(400px, 100%);
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 32px 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 3px solid var(--color-border);
  border-radius: 22px;
  box-shadow: var(--shadow-outer);
  text-align: center;
}

.login-logo {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  border: 4px solid #fff;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-sun));
  box-shadow: var(--shadow-outer);
  color: #fff;
  font-family: 'Fredoka', sans-serif;
  font-size: 30px;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-family: 'Fredoka', sans-serif;
  font-size: 24px;
  color: var(--color-foreground);
}

.mode-tabs {
  display: flex;
  gap: 8px;
}

.mode-tab {
  flex: 1;
  padding: 9px 0;
  border: 2px solid var(--color-border);
  border-radius: 999px;
  background: #fff;
  color: var(--color-foreground);
  font-weight: 700;
  cursor: pointer;
}

.mode-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.field :deep(.el-input__wrapper) {
  border: 2px solid var(--color-border);
  border-radius: 12px;
  box-shadow: none;
}

.submit-btn {
  width: 100%;
}
</style>
