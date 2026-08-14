<template>
  <!-- 全局布局：顶部导航 + 内容区，所有页面共用 -->
  <div class="layout">
    <header class="header">
      <div class="brand">
        <span class="brand-logo">A</span>
        <span class="brand-name">AIGC 对话平台</span>
      </div>
      <nav class="nav">
        <router-link
          to="/"
          class="nav-item"
          :class="{ active: $route.path === '/' }"
        >
          首页
        </router-link>
        <router-link
          to="/chat"
          class="nav-item"
          :class="{ active: $route.path === '/chat' }"
        >
          聊天
        </router-link>
        <router-link
          to="/upload"
          class="nav-item"
          :class="{ active: $route.path === '/upload' }"
        >
          文档上传
        </router-link>
      </nav>
    </header>
    <main class="content">
      <!-- 路由出口：当前地址对应的页面组件渲染在这里 -->
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f6f7;
}

.header {
  height: 56px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: linear-gradient(135deg, #4e6ef2, #7b5cff);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
}

.brand-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2329;
}

.nav {
  display: flex;
  gap: 6px;
}

.nav-item {
  padding: 7px 14px;
  border-radius: 8px;
  color: #4e5969;
  font-size: 14px;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-item:hover {
  background: #f2f3f5;
  color: #1f2329;
}

.nav-item.active {
  background: #eef3ff;
  color: #4e6ef2;
  font-weight: 600;
}

.content {
  flex: 1;
  min-height: 0;
  padding: 0;
}
</style>
