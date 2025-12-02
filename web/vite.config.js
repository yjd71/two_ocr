import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'


export default defineConfig({
   server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000', // 将 /api 请求代理到后端服务
        '/uploads': 'http://127.0.0.1:8000' // 新增：代理静态图片目录
    },
  },
  plugins: [
    vue(),
  ]
})
