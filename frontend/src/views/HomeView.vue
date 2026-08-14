<template>
  <!-- 首页：项目入口，保持简洁的产品首屏 -->
  <div class="home">
    <div class="hero">
      <span class="hero-logo">A</span>
      <h1>AIGC 对话平台</h1>
      <p>多模型对话 · RAG 知识库 · AI 长期记忆</p>
      <div class="actions">
        <el-button type="primary" size="large" class="action-btn" @click="$router.push('/chat')">
          进入聊天
        </el-button>
        <el-button size="large" class="action-btn" @click="$router.push('/upload')">
          文档上传
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.hero {
  text-align: center;
}

.hero-logo {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #4e6ef2, #7b5cff);
  color: #fff;
  font-size: 30px;
  font-weight: 700;
}

h1 {
  margin: 0 0 10px;
  font-size: 28px;
  font-weight: 700;
  color: #1f2329;
}

p {
  margin: 0 0 28px;
  font-size: 14px;
  color: #86909c;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.action-btn {
  min-width: 120px;
}
</style>
