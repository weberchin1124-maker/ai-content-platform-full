import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // ✅ 新增這段 server 設定，讓前端知道後端在哪裡
  server: {
    proxy: {
      // 只要前端呼叫的網址是 /api 開頭 (例如 /api/auth/login)
      '/api': {
        target: 'http://127.0.0.1:5000', // 自動轉發給 Flask 後端
        changeOrigin: true,
        secure: false,
      },
    },
  },
})