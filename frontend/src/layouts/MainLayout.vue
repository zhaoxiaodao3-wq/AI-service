<template>
  <!-- 全局布局：顶部导航 + 内容区，所有页面共用 -->
  <el-container class="layout">
    <el-header class="header">
      <div class="brand">AIGC 对话平台</div>
      <!-- 横向菜单：:router="true" 让菜单项点击时跳转到对应路由 -->
      <el-menu
        mode="horizontal"
        :router="true"
        :default-active="$route.path"
        class="nav"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/chat">聊天</el-menu-item>
        <el-menu-item index="/upload">文档上传</el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="content">
      <!-- 路由出口：当前地址对应的页面组件渲染在这里 -->
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color-light);
}

.brand {
  font-size: 18px;
  font-weight: 600;
}

.content {
  padding: 24px;
}
</style>
