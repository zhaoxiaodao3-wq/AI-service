import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // 注册 Vue 插件，让 Vite 能编译 .vue 单文件组件
  plugins: [vue()],
  server: {
    // 前端开发服务器端口；与后端 CORS 配置保持一致
    port: 5173,
    proxy: {
      // 凡是以 /api 开头的请求，都转发到后端 8000 端口。
      // 这样前端代码里写 /api/xxx 即可，浏览器不产生跨域问题。
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
