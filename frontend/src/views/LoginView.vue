<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold mb-6 text-center">OpenClawHub 登录</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">邮箱</label>
          <input
            v-model="email"
            type="email"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="your@email.com"
            required
          />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 mb-2">密码</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="••••••••"
            required
          />
        </div>
        <button
          type="submit"
          class="w-full bg-primary text-white py-2 rounded-lg hover:bg-opacity-90 transition"
        >
          登录
        </button>
      </form>
      <p class="mt-4 text-center text-gray-600">
        还没有账号?
        <router-link to="/register" class="text-primary hover:underline">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = () => {
  // TODO: 实现登录逻辑
  console.log('Login:', email.value, password.value)
  router.push('/projects')
}
</script>
