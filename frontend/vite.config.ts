import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8008',
          changeOrigin: true
        },
        '/ws': {
          target: env.VITE_API_PROXY_TARGET?.replace(/^http/, 'ws') || 'ws://localhost:8008',
          ws: true
        }
      }
    }
  }
})
