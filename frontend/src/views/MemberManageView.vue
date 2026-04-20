<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">成员管理</h2>
        <div class="flex gap-3">
          <button
            @click="router.push(`/orgs/${route.params.id}`)"
            class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            返回组织
          </button>
          <button
            @click="showInvite = true"
            class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
          >
            邀请成员
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-sm text-gray-300">昵称</th>
              <th class="px-4 py-3 text-left text-sm text-gray-300">邮箱</th>
              <th class="px-4 py-3 text-left text-sm text-gray-300">角色</th>
              <th class="px-4 py-3 text-right text-sm text-gray-300">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr v-for="member in orgStore.members" :key="member.userId" class="hover:bg-gray-750">
              <td class="px-4 py-3 text-white">{{ member.userName }}</td>
              <td class="px-4 py-3 text-gray-400">{{ member.userEmail }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 text-xs rounded-full" :class="member.role === 'admin' ? 'bg-purple-500/20 text-purple-400' : 'bg-gray-600/50 text-gray-300'">
                  {{ member.role === 'admin' ? '管理员' : '成员' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  v-if="member.role !== 'owner'"
                  @click="handleRemove(member.userId)"
                  class="text-sm text-red-400 hover:text-red-300"
                >
                  移除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Invite Modal -->
      <div v-if="showInvite" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showInvite = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">邀请成员</h3>
          <form @submit.prevent="handleInvite">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">邮箱</label>
              <input
                v-model="inviteForm.email"
                type="email"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="member@example.com"
                required
              />
            </div>
            <p v-if="inviteError" class="mb-4 text-sm text-red-400">{{ inviteError }}</p>
            <p v-if="inviteSuccess" class="mb-4 text-sm text-green-400">邀请已发送</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="inviteLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ inviteLoading ? '发送中...' : '发送邀请' }}
              </button>
              <button
                type="button"
                @click="showInvite = false"
                class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrgStore } from '@/stores/org'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const orgStore = useOrgStore()
const loading = ref(false)
const showInvite = ref(false)
const inviteLoading = ref(false)
const inviteError = ref('')
const inviteSuccess = ref(false)
const inviteForm = ref({ email: '' })

onMounted(async () => {
  loading.value = true
  await orgStore.fetchMembers(String(route.params.id))
  loading.value = false
})

const handleRemove = async (userId: string) => {
  await orgStore.removeMember(String(route.params.id), userId)
}

const handleInvite = async () => {
  inviteLoading.value = true
  inviteError.value = ''
  inviteSuccess.value = false
  try {
    await orgStore.inviteMember(String(route.params.id), inviteForm.value.email)
    inviteSuccess.value = true
    inviteForm.value = { email: '' }
    setTimeout(() => {
      showInvite.value = false
      inviteSuccess.value = false
    }, 1500)
  } catch (e) {
    inviteError.value = '邀请失败'
  } finally {
    inviteLoading.value = false
  }
}
</script>
