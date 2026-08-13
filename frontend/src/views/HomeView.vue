<template>
  <!-- 首页：项目入口导航 -->
  <div class="home">
    <h1>AIGC 对话 + RAG + AI 记忆项目</h1>
    <p>阶段零：环境搭建与架构初始化</p>
    <!-- 两个入口按钮：跳转到聊天页和文档上传页 -->
    <el-space>
      <el-button type="primary" @click="$router.push('/chat')">进入聊天</el-button>
      <el-button @click="$router.push('/upload')">文档上传</el-button>
    </el-space>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding-top: 80px;
}
</style>
