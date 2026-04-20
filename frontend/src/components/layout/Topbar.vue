<template>
  <header class="h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6">
    <div class="text-lg font-semibold text-white">{{ title }}</div>
    <div class="flex items-center gap-4">
      <span class="text-gray-400 text-sm">{{ user?.name }}</span>
      <button
        @click="handleLogout"
        class="px-4 py-1.5 text-sm bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
      >
        退出
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const title = computed(() => {
  const titles: Record<string, string> = {
    OrgList: '我的组织',
    OrgDetail: '组织详情',
    MemberManage: '成员管理',
    Settings: '个人设置',
  }
  return titles[String(route.name)] || ''
})

const user = computed(() => authStore.user)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
