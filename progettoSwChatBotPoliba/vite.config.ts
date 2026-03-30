import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 4201,
    host: '127.0.0.1',
    proxy: {
      '/chat': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
