<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="bg-gray-800 p-8 rounded-xl shadow-lg w-96 border border-gray-700">
      <div v-if="loading" class="text-center text-gray-400">验证中...</div>
      <div v-else-if="error" class="text-center">
        <p class="text-red-400 mb-4">{{ error }}</p>
        <router-link to="/login" class="text-purple-500 hover:underline">返回登录</router-link>
      </div>
      <div v-else>
        <h1 class="text-2xl font-bold mb-4 text-white text-center">加入组织</h1>
        <p class="text-gray-400 mb-6 text-center">
          您已被邀请加入 <span class="text-purple-500">{{ invitation?.orgName }}</span>
        </p>
        <button
          @click="handleAccept"
          :disabled="accepting"
          class="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition disabled:opacity-50"
        >
          {{ accepting ? '接受中...' : '接受邀请' }}
        </button>
        <p v-if="success" class="mt-4 text-center text-green-400">已成功加入组织!</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrgStore } from '@/stores/org'

const route = useRoute()
const router = useRouter()
const orgStore = useOrgStore()

const loading = ref(true)
const accepting = ref(false)
const error = ref('')
const success = ref(false)
const invitation = ref<{ orgName: string | null; valid: boolean } | null>(null)

onMounted(async () => {
  try {
    const data = await orgStore.checkInvitation(String(route.params.token))
    invitation.value = data
  } catch (e) {
    error.value = '邀请无效或已过期'
  } finally {
    loading.value = false
  }
})

const handleAccept = async () => {
  accepting.value = true
  error.value = ''
  try {
    await orgStore.acceptInvite(String(route.params.token))
    success.value = true
    setTimeout(() => router.push('/orgs'), 1500)
  } catch (e) {
    error.value = '接受失败，请重试'
  } finally {
    accepting.value = false
  }
}
</script>
