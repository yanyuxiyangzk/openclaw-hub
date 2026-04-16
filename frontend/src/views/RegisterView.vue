<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold mb-6 text-center">注册 OpenClawHub</h1>
      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">姓名</label>
          <input
            v-model="name"
            type="text"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Your Name"
            required
          />
        </div>
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
          注册
        </button>
      </form>
      <p class="mt-4 text-center text-gray-600">
        已有账号?
        <router-link to="/login" class="text-primary hover:underline">登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const name = ref('')
const email = ref('')
const password = ref('')
const router = useRouter()

const handleRegister = () => {
  // TODO: 实现注册逻辑
  console.log('Register:', name.value, email.value, password.value)
  router.push('/login')
}
</script>
