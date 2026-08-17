<template>
  <!-- 二次元卡通全局布局：顶部导航 + 内容区 -->
  <div class="layout">
    <header class="header">
      <div class="brand">
        <span class="brand-logo">A</span>
        <span class="brand-name">AIGC 对话平台</span>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          首页
        </router-link>
        <router-link to="/chat" class="nav-item" :class="{ active: $route.path === '/chat' }">
          聊天
        </router-link>
        <router-link to="/upload" class="nav-item" :class="{ active: $route.path === '/upload' }">
          文档上传
        </router-link>
      </nav>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  height: 64px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: var(--border-w) solid var(--color-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #fff;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-sun));
  box-shadow: var(--shadow-outer);
  color: #fff;
  font-family: 'Fredoka', sans-serif;
  font-size: 18px;
  font-weight: 700;
}

.brand-name {
  font-family: 'Fredoka', sans-serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-foreground);
}

.nav {
  display: flex;
  gap: 8px;
}

.nav-item {
  padding: 9px 16px;
  border: 2px solid var(--color-border);
  border-radius: 999px;
  color: var(--color-foreground);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.nav-item:hover {
  background: var(--color-muted);
  transform: translateY(-1px);
}

.nav-item.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
  box-shadow: var(--shadow-outer);
}

.content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 0;
}
</style>
