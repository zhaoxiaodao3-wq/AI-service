import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '../layouts/MainLayout.vue'
import HomeView from '../views/HomeView.vue'
import ChatView from '../views/ChatView.vue'
import UploadView from '../views/UploadView.vue'

// 创建路由实例：createWebHistory 使用 HTML5 History 模式，地址栏是 /chat 而不是 /#/chat
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      // 所有页面共用 MainLayout 布局（顶部导航 + 内容区）
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'home', component: HomeView }, // 首页
        { path: 'chat', name: 'chat', component: ChatView }, // 聊天页
        { path: 'upload', name: 'upload', component: UploadView }, // 文档上传页
      ],
    },
  ],
})

export default router
