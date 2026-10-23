import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.DEV_API_TARGET || 'http://127.0.0.1:8000'
  return {
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // 开发时把 /api 请求代理到 Django 后端
      '/api': {
        target,
        changeOrigin: true,
      },
      // 媒体文件也代理
      '/media': {
        target,
        changeOrigin: true,
      },
    },
  },
  }
})
