<template>
  <!-- 文档上传页：阶段 3 实现 PDF/TXT/MD 上传与解析，目前只有静态占位 -->
  <div class="upload">
    <div class="upload-box">
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <p>文档上传将在阶段 3 接入</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.upload {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.upload-box {
  width: min(520px, 100%);
  min-height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: #fff;
  border: 1px dashed #c9cdd4;
  border-radius: 8px;
  color: #86909c;
}

.upload-icon {
  font-size: 44px;
  color: #4e6ef2;
}

p {
  margin: 0;
  font-size: 14px;
}
</style>
