<template>
  <AppLayout>
    <div class="max-w-2xl">
      <h2 class="text-2xl font-bold text-white mb-6">个人设置</h2>
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <form @submit.prevent="handleUpdate">
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">昵称</label>
            <input
              v-model="form.name"
              type="text"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">邮箱</label>
            <input
              v-model="form.email"
              type="email"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          <p v-if="success" class="mb-4 text-sm text-green-400">保存成功</p>
          <p v-if="error" class="mb-4 text-sm text-red-400">{{ error }}</p>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition disabled:opacity-50"
            >
              {{ loading ? '保存中...' : '保存' }}
            </button>
            <button
              type="button"
              @click="handleLogout"
              class="px-6 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
            >
              退出登录
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ name: '', email: '' })
const loading = ref(false)
const success = ref(false)
const error = ref('')

onMounted(async () => {
  await authStore.fetchMe()
  if (authStore.user) {
    form.value = { name: authStore.user.name, email: authStore.user.email }
  }
})

const handleUpdate = async () => {
  loading.value = true
  success.value = false
  error.value = ''
  try {
    await authStore.updateUser(form.value)
    success.value = true
  } catch (e) {
    error.value = '保存失败'
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
