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
          <h2 class="text-2xl font-bold text-white">{{ agentStore.currentAgent?.name }}</h2>
          <span
            v-if="agentStore.currentAgent"
            :class="{
              'bg-green-500/20 text-green-400': agentStore.currentAgent.status === 'online',
              'bg-yellow-500/20 text-yellow-400': agentStore.currentAgent.status === 'busy',
              'bg-red-500/20 text-red-400': agentStore.currentAgent.status === 'error',
              'bg-gray-500/20 text-gray-400': agentStore.currentAgent.status === 'offline',
            }"
            class="px-2 py-1 rounded text-xs font-medium"
          >
            {{ statusText(agentStore.currentAgent.status) }}
          </span>
        </div>
        <div class="flex gap-2">
          <button
            @click="handleStart"
            :disabled="agentStore.currentAgent?.status === 'online'"
            class="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 disabled:opacity-50 transition"
          >
            启动
          </button>
          <button
            @click="handleStop"
            :disabled="agentStore.currentAgent?.status === 'offline'"
            class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 disabled:opacity-50 transition"
          >
            停止
          </button>
          <button
            @click="showEdit = true"
            class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            编辑
          </button>
          <button
            @click="handleDelete"
            class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition"
          >
            删除
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <template v-else-if="agentStore.currentAgent">
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <p class="text-gray-400">{{ agentStore.currentAgent.description || '暂无描述' }}</p>
          <div class="flex items-center gap-6 mt-4">
            <span class="text-gray-500 text-sm">类型: {{ agentStore.currentAgent.agent_type }}</span>
            <span class="text-gray-500 text-sm">创建于 {{ formatDate(agentStore.currentAgent.created_at) }}</span>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex gap-4 mb-6 border-b border-gray-700 pb-4">
          <router-link
            :to="`/agents/${agentId}`"
            class="text-white font-medium pb-2 border-b-2 border-purple-500"
          >
            概览
          </router-link>
          <router-link
            :to="`/agents/${agentId}/config`"
            class="text-gray-400 hover:text-white pb-2 border-b-2 border-transparent hover:border-gray-600 transition"
          >
            配置
          </router-link>
          <router-link
            :to="`/agents/${agentId}/memory`"
            class="text-gray-400 hover:text-white pb-2 border-b-2 border-transparent hover:border-gray-600 transition"
          >
            记忆
          </router-link>
          <router-link
            :to="`/agents/${agentId}/metrics`"
            class="text-gray-400 hover:text-white pb-2 border-b-2 border-transparent hover:border-gray-600 transition"
          >
            指标
          </router-link>
        </div>

        <!-- Health Info -->
        <div v-if="agentStore.agentHealth" class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <h3 class="text-lg font-semibold text-white mb-4">健康状态</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-white">{{ agentStore.agentHealth.healthy ? '健康' : '异常' }}</div>
              <div class="text-gray-500 text-sm">状态</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-white">{{ agentStore.agentHealth.cpu_percent?.toFixed(1) || '-' }}%</div>
              <div class="text-gray-500 text-sm">CPU</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-white">{{ agentStore.agentHealth.memory_mb?.toFixed(1) || '-' }} MB</div>
              <div class="text-gray-500 text-sm">内存</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-white">{{ formatUptime(agentStore.agentHealth.uptime_seconds) }}</div>
              <div class="text-gray-500 text-sm">运行时长</div>
            </div>
          </div>
        </div>

        <!-- Logs -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white">日志</h3>
            <button
              @click="loadLogs"
              class="px-3 py-1 text-sm bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
            >
              刷新
            </button>
          </div>

          <div v-if="agentStore.agentLogs && agentStore.agentLogs.logs.length === 0" class="text-gray-400 text-center py-4">
            暂无日志
          </div>
          <div v-else-if="agentStore.agentLogs" class="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-80 overflow-y-auto">
            <div
              v-for="(log, idx) in agentStore.agentLogs.logs"
              :key="idx"
              class="flex gap-3 py-1"
            >
              <span class="text-gray-500">{{ formatLogTime(log.timestamp) }}</span>
              <span
                :class="{
                  'text-green-400': log.level === 'INFO',
                  'text-yellow-400': log.level === 'WARNING',
                  'text-red-400': log.level === 'ERROR',
                }"
              >
                [{{ log.level }}]
              </span>
              <span class="text-gray-300">{{ log.message }}</span>
            </div>
          </div>
          <div v-else class="text-gray-400 text-center py-4">
            点击刷新加载日志
          </div>
        </div>
      </template>

      <!-- Edit Modal -->
      <div v-if="showEdit" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showEdit = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">编辑 Agent</h3>
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
                rows="3"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAgentStore } from '@/stores/agent'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = useRouter()
const route = useRoute()
const agentStore = useAgentStore()
const loading = ref(false)
const showEdit = ref(false)
const updateLoading = ref(false)
const updateError = ref('')
const editForm = ref({ name: '', description: '' })

const agentId = computed(() => route.params.id as string)

onMounted(async () => {
  loading.value = true
  await agentStore.fetchAgent(agentId.value)
  if (agentStore.currentAgent) {
    editForm.value = {
      name: agentStore.currentAgent.name,
      description: agentStore.currentAgent.description || '',
    }
  }
  await loadHealth()
  await loadLogs()
  loading.value = false
})

const loadHealth = async () => {
  try {
    await agentStore.fetchHealth(agentId.value)
  } catch {}
}

const loadLogs = async () => {
  try {
    await agentStore.fetchLogs(agentId.value)
  } catch {}
}

const handleUpdate = async () => {
  updateLoading.value = true
  updateError.value = ''
  try {
    await agentStore.updateAgent(agentId.value, editForm.value)
    showEdit.value = false
  } catch (e) {
    updateError.value = '更新失败'
  } finally {
    updateLoading.value = false
  }
}

const handleStart = async () => {
  await agentStore.startAgent(agentId.value)
  await agentStore.fetchAgent(agentId.value)
  await loadHealth()
}

const handleStop = async () => {
  await agentStore.stopAgent(agentId.value)
  await agentStore.fetchAgent(agentId.value)
  await loadHealth()
}

const handleDelete = async () => {
  if (!confirm('确定要删除此 Agent 吗？')) return
  await agentStore.deleteAgent(agentId.value)
  router.push('/agents')
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

const formatUptime = (seconds: number | null) => {
  if (!seconds) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h}h ${m}m ${s}s`
}

const formatLogTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}
</script>