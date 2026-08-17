<template>
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
  width: 76px;
  height: 76px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 22px;
  border: 4px solid #fff;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-sun));
  box-shadow: var(--shadow-outer);
  color: #fff;
  font-family: 'Fredoka', sans-serif;
  font-size: 36px;
  font-weight: 700;
}

h1 {
  margin: 0 0 10px;
  font-size: 40px;
  font-weight: 700;
  color: var(--color-foreground);
}

p {
  margin: 0 0 30px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-primary);
}

.actions {
  display: flex;
  justify-content: center;
  gap: 14px;
}

.action-btn {
  min-width: 130px;
}
</style>
