import axios from 'axios'
import { ElMessage } from 'element-plus'

// 统一请求封装：所有接口都走这个实例，便于统一 baseURL、超时、错误提示。
// baseURL 取环境变量 VITE_API_BASE（开发环境是 /api，由 Vite 代理到后端）。
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000, // 30 秒超时，防止请求一直挂起
})

// 请求拦截器：在请求发出前统一处理。
// 阶段 2 接入登录后，在这里给每个请求自动带上 Token。
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一处理成功与失败。
// 成功时直接返回后端 data 字段；失败时弹错误提示并继续 reject。
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const path = error?.config?.url || ''
    if (
      error?.response?.status === 401 &&
      !path.includes('/auth/login') &&
      !path.includes('/auth/register')
    ) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('username')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    // 优先取后端返回的业务错误信息，取不到就用通用提示
    ElMessage.error(error?.response?.data?.message || '网络异常，请稍后重试')
    return Promise.reject(error)
  },
)

export default request
