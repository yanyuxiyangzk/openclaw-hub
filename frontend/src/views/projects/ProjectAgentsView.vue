<template>
  <AppLayout>
    <div class="max-w-5xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push(`/projects/${projectId}`)" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">{{ projectStore.currentProject?.name }} — 数字员工</h2>
        </div>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          绑定 Agent
        </button>
      </div>

      <div v-if="loading" class="text-gray-400 py-8 text-center">加载中...</div>
      <div v-else-if="!agents.length" class="text-gray-400 text-center py-12">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p>暂无绑定的数字员工</p>
        <p class="text-sm mt-1">点击右上角按钮绑定 Agent</p>
      </div>
      <div v-else class="grid grid-cols-2 gap-4">
        <div
          v-for="agent in agents"
          :key="agent.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition cursor-pointer"
          @click="router.push(`/agents/${agent.id}`)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-white">{{ agent.name }}</h3>
                <span
                  :class="statusClass(agent.status)"
                  class="px-2 py-0.5 rounded text-xs font-medium"
                >
                  {{ statusText(agent.status) }}
                </span>
              </div>
              <div class="text-sm text-gray-400">
                <span class="mr-4">角色: {{ agent.role || '未设置' }}</span>
                <span>任务: {{ agent.task_count || 0 }}</span>
              </div>
            </div>
            <button
              @click.stop="handleUnbind(agent.id)"
              class="p-1.5 text-gray-500 hover:text-red-400 transition"
              title="解除绑定"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 绑定 Agent 弹窗 -->
      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[520px] border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">绑定数字员工</h3>
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">选择 Agent</label>
            <select
              v-model="selectedAgentId"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="" disabled>选择 Agent</option>
              <option v-for="a in availableAgents" :key="a.id" :value="a.id">
                {{ a.name }} ({{ a.status }})
              </option>
            </select>
          </div>
          <div class="flex gap-3">
            <button
              @click="handleBind"
              :disabled="!selectedAgentId || binding"
              class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
            >
              {{ binding ? '绑定中...' : '绑定' }}
            </button>
            <button
              @click="showCreate = false"
              class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useProjectStore } from '@/stores/project'
import { getProjectAgents, assignAgentToProject, removeAgentFromProject, getAvailableAgents } from '@/api/projects'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string
const projectStore = useProjectStore()
const agentStore = useAgentStore()

const agents = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const selectedAgentId = ref('')
const binding = ref(false)

const availableAgents = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  await Promise.all([
    projectStore.fetchProject(projectId),
    fetchProjectAgents(),
    fetchAvailableAgents(),
  ])
  loading.value = false
})

const fetchProjectAgents = async () => {
  try {
    const res = await getProjectAgents(projectId)
    agents.value = res.data.data.items || []
  } catch (e) {
    console.error('Failed to fetch project agents:', e)
  }
}

const fetchAvailableAgents = async () => {
  try {
    const res = await getAvailableAgents(projectId)
    availableAgents.value = res.data.data || []
  } catch (e) {
    console.error('Failed to fetch available agents:', e)
  }
}

const handleBind = async () => {
  if (!selectedAgentId.value) return
  binding.value = true
  try {
    await assignAgentToProject(projectId, { agent_id: selectedAgentId.value })
    showCreate.value = false
    selectedAgentId.value = ''
    await Promise.all([fetchProjectAgents(), fetchAvailableAgents()])
  } catch (e) {
    console.error('Failed to bind agent:', e)
  } finally {
    binding.value = false
  }
}

const handleUnbind = async (agentId: string) => {
  if (!confirm('确定要解除绑定吗？')) return
  try {
    await removeAgentFromProject(projectId, agentId)
    await Promise.all([fetchProjectAgents(), fetchAvailableAgents()])
  } catch (e) {
    console.error('Failed to unbind agent:', e)
  }
}

const statusClass = (status: string) => ({
  'bg-green-500/20 text-green-400': status === 'active',
  'bg-yellow-500/20 text-yellow-400': status === 'idle',
  'bg-gray-500/20 text-gray-400': status === 'offline',
})

const statusText = (status: string) => ({
  active: '运行中', idle: '空闲', offline: '离线'
}[status] || status)
</script>
