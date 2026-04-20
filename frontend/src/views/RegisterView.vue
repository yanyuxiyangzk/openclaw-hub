<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="bg-gray-800 p-8 rounded-xl shadow-lg w-96 border border-gray-700">
      <h1 class="text-2xl font-bold mb-6 text-center text-white">注册 OpenClawHub</h1>
      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label class="block text-gray-400 mb-2 text-sm">昵称</label>
          <input
            v-model="name"
            type="text"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Your Name"
            required
          />
        </div>
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
        <div class="mb-4">
          <label class="block text-gray-400 mb-2 text-sm">密码</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="••••••••"
            required
          />
          <p class="mt-1 text-xs" :class="passwordStrength.color">{{ passwordStrength.text }}</p>
        </div>
        <div class="mb-6">
          <label class="block text-gray-400 mb-2 text-sm">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="••••••••"
            required
          />
          <p v-if="confirmPassword && password !== confirmPassword" class="mt-1 text-xs text-red-400">密码不匹配</p>
        </div>
        <p v-if="error" class="mb-4 text-sm text-red-400">{{ error }}</p>
        <button
          type="submit"
          :disabled="loading || Boolean(confirmPassword && password !== confirmPassword)"
          class="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="mt-4 text-center text-gray-400 text-sm">
        已有账号?
        <router-link to="/login" class="text-purple-500 hover:underline">登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()
const authStore = useAuthStore()

const passwordStrength = computed(() => {
  const p = password.value
  if (!p) return { text: '', color: 'text-gray-500' }
  if (p.length < 6) return { text: '密码太短 (至少6位)', color: 'text-red-400' }
  if (p.length < 8) return { text: '密码强度: 中', color: 'text-yellow-400' }
  return { text: '密码强度: 强', color: 'text-green-400' }
})

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = '密码不匹配'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await authStore.register(name.value, email.value, password.value)
    router.push('/orgs')
  } catch (e) {
    error.value = '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
