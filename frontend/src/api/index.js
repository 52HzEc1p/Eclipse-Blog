import axios from 'axios'

// 创建 Axios 实例
const api = axios.create({
  baseURL: '/api',  // Vite 会代理到 Django
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 — 未来可以在这里加 token
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// 响应拦截器 — 统一处理错误
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

// === 文章 API ===
export const getPosts = (params) => api.get('/posts/', { params })
export const getPost = (slug) => api.get(`/posts/${slug}/`)
export const getFeaturedPosts = () => api.get('/posts/featured/')

// === About 页面 API ===
export const getAboutPage = () => api.get('/about/')
export const getSectionPage = (section) => api.get(`/section-pages/${section}/`)

// === 分类 API ===
export const getCategories = (params) => api.get('/categories/', { params })

// === 标签 API ===
export const getTags = () => api.get('/tags/')

export default api
