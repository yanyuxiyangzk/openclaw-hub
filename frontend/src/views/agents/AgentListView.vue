<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">Agent 管理</h2>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建 Agent
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="agentStore.agents.length === 0" class="text-gray-400 text-center py-8">
        暂无 Agent，点击上方按钮创建
      </div>
      <div v-else class="grid gap-4">
        <div
          v-for="agent in agentStore.agents"
          :key="agent.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition cursor-pointer"
          @click="router.push(`/agents/${agent.id}`)"
        >
          <div class="flex items-start justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white">{{ agent.name }}</h3>
              <p class="text-gray-400 text-sm mt-1">{{ agent.description || '暂无描述' }}</p>
            </div>
            <span
              :class="{
                'bg-green-500/20 text-green-400': agent.status === 'online',
                'bg-yellow-500/20 text-yellow-400': agent.status === 'busy',
                'bg-red-500/20 text-red-400': agent.status === 'error',
                'bg-gray-500/20 text-gray-400': agent.status === 'offline',
              }"
              class="px-2 py-1 rounded text-xs font-medium"
            >
              {{ statusText(agent.status) }}
            </span>
          </div>
          <div class="flex items-center gap-4 mt-3">
            <span class="text-gray-500 text-xs">类型: {{ agent.agent_type }}</span>
            <span class="text-gray-500 text-xs">创建于 {{ formatDate(agent.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Create Modal -->
      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[480px] border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">创建 Agent</h3>
          <form @submit.prevent="handleCreate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">Agent 名称</label>
              <input
                v-model="newAgent.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">描述</label>
              <textarea
                v-model="newAgent.description"
                rows="2"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              ></textarea>
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">Agent 类型</label>
              <select
                v-model="newAgent.agent_type"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="hermes">Hermes</option>
              </select>
            </div>
            <p v-if="createError" class="mb-4 text-sm text-red-400">{{ createError }}</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="createLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ createLoading ? '创建中...' : '创建' }}
              </button>
              <button
                type="button"
                @click="showCreate = false"
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
import { useAgentStore } from '@/stores/agent'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = useRouter()
const agentStore = useAgentStore()
const loading = ref(false)
const showCreate = ref(false)
const createLoading = ref(false)
const createError = ref('')
const newAgent = ref({ name: '', description: '', agent_type: 'hermes' })

onMounted(async () => {
  loading.value = true
  await agentStore.fetchAgents()
  loading.value = false
})

const handleCreate = async () => {
  createLoading.value = true
  createError.value = ''
  try {
    await agentStore.createAgent(newAgent.value)
    showCreate.value = false
    newAgent.value = { name: '', description: '', agent_type: 'hermes' }
  } catch (e) {
    createError.value = '创建失败'
  } finally {
    createLoading.value = false
  }
}

const statusText = (status: string) => {
  const map: Record<string, string> = {
    online: '在线',
    busy: '忙碌',
    error: '错误',
    offline: '离线',
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>