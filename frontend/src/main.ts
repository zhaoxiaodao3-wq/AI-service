import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import './style.css'
import App from './App.vue'
import router from './router'

// 创建应用实例，注册路由和 Element Plus，再挂载到 index.html 的 #app
createApp(App).use(router).use(ElementPlus).mount('#app')
