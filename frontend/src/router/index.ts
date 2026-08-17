import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import MainLayout from '../layouts/MainLayout.vue'
import HomeView from '../views/HomeView.vue'
import ChatView from '../views/ChatView.vue'
import UploadView from '../views/UploadView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'home', component: HomeView },
        { path: 'chat', name: 'chat', component: ChatView },
        { path: 'upload', name: 'upload', component: UploadView },
      ],
    },
  ],
})

// 路由守卫：未登录跳登录页，已登录访问登录页跳聊天
router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (to.path !== '/login' && !token) {
    return { path: '/login' }
  }
  if (to.path === '/login' && token) {
    return { path: '/chat' }
  }
  return true
})

export default router
