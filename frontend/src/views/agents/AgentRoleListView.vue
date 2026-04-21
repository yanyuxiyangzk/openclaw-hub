<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push('/agents')" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">角色模板</h2>
        </div>
        <button
          @click="router.push('/agent-roles/new')"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建角色
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="roles.length === 0" class="bg-gray-800 rounded-xl p-8 border border-gray-700 text-center">
        <div class="text-gray-400 mb-4">暂无角色模板</div>
        <button
          @click="router.push('/agent-roles/new')"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建第一个角色
        </button>
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="role in roles"
          :key="role.id"
          class="bg-gray-800 rounded-xl p-6 border border-gray-700"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-white mb-2">{{ role.name }}</h3>
              <p class="text-gray-400 text-sm mb-4">{{ role.description || '暂无描述' }}</p>
              <div class="flex items-center gap-4 text-gray-500 text-sm">
                <span>创建于 {{ formatDate(role.created_at) }}</span>
                <span v-if="role.system_prompt_template">已配置系统提示词</span>
              </div>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                @click="handleEdit(role)"
                class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
              >
                编辑
              </button>
              <button
                @click="handleDelete(role)"
                class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="showEdit" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showEdit = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[500px] border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">编辑角色</h3>
          <form @submit.prevent="handleUpdate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">名称</label>
              <input
                v-model="editForm.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">描述</label>
              <textarea
                v-model="editForm.description"
                rows="2"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              ></textarea>
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">系统提示词模板</label>
              <textarea
                v-model="editForm.system_prompt_template"
                rows="4"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              ></textarea>
            </div>
            <p v-if="updateError" class="mb-4 text-sm text-red-400">{{ updateError }}</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="updateLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ updateLoading ? '保存中...' : '保存' }}
              </button>
              <button
                type="button"
                @click="showEdit = false"
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
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import * as phase3Api from '@/api/phase3'
import type { AgentRole } from '@/types'

const router = useRouter()
const loading = ref(false)
const roles = ref<AgentRole[]>([])
const showEdit = ref(false)
const updateLoading = ref(false)
const updateError = ref('')
const editForm = ref({ name: '', description: '', system_prompt_template: '' })
const editingRole = ref<AgentRole | null>(null)

onMounted(async () => {
  await loadRoles()
})

const loadRoles = async () => {
  loading.value = true
  try {
    const res = await phase3Api.listAgentRoles()
    roles.value = res.data.data
  } catch {
    roles.value = []
  } finally {
    loading.value = false
  }
}

const handleEdit = (role: AgentRole) => {
  editingRole.value = role
  editForm.value = {
    name: role.name,
    description: role.description || '',
    system_prompt_template: role.system_prompt_template || '',
  }
  showEdit.value = true
}

const handleUpdate = async () => {
  if (!editingRole.value) return
  updateLoading.value = true
  updateError.value = ''
  try {
    await phase3Api.updateAgentRole(editingRole.value.id, editForm.value)
    showEdit.value = false
    await loadRoles()
  } catch {
    updateError.value = '更新失败'
  } finally {
    updateLoading.value = false
  }
}

const handleDelete = async (role: AgentRole) => {
  if (!confirm(`确定要删除角色 "${role.name}" 吗？`)) return
  try {
    await phase3Api.deleteAgentRole(role.id)
    await loadRoles()
  } catch {}
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>