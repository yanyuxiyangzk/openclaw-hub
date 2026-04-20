<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="bg-gray-800 p-8 rounded-xl shadow-lg w-96 border border-gray-700">
      <h1 class="text-2xl font-bold mb-6 text-center text-white">OpenClawHub 登录</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-400 mb-2 text-sm">邮箱</label>
          <input
            v-model="email"
            type="email"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="your@email.com"
            required
          />
        </div>
        <div class="mb-6">
          <label class="block text-gray-400 mb-2 text-sm">密码</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="••••••••"
            required
          />
        </div>
        <p v-if="error" class="mb-4 text-sm text-red-400">{{ error }}</p>
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="mt-4 text-center text-gray-400 text-sm">
        还没有账号?
        <router-link to="/register" class="text-purple-500 hover:underline">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(email.value, password.value)
    router.push('/orgs')
  } catch (e) {
    error.value = '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}
</script>
