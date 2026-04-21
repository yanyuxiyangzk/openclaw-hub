<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push(`/agents/${agentId}`)" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">Agent 记忆</h2>
        </div>
        <button
          @click="handleResetState"
          class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition"
        >
          重置状态
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <template v-else>
        <!-- Memory Config -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <h3 class="text-lg font-semibold text-white mb-4">记忆配置</h3>
          <form @submit.prevent="handleUpdateMemory">
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-gray-400 mb-2 text-sm">记忆类型</label>
                <select
                  v-model="memoryForm.memory_type"
                  class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="shortterm">短期记忆</option>
                  <option value="longterm">长期记忆</option>
                  <option value="hybrid">混合记忆</option>
                </select>
              </div>
              <div>
                <label class="block text-gray-400 mb-2 text-sm">最大上下文 Token</label>
                <input
                  v-model.number="memoryForm.max_context_tokens"
                  type="number"
                  min="0"
                  class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label class="block text-gray-400 mb-2 text-sm">上下文窗口</label>
                <input
                  v-model.number="memoryForm.context_window"
                  type="number"
                  min="0"
                  class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label class="flex items-center gap-2 text-gray-400 mt-6">
                  <input v-model="memoryForm.persist_context" type="checkbox" class="rounded" />
                  持久化上下文
                </label>
              </div>
            </div>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="updateLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 transition"
              >
                {{ updateLoading ? '保存中...' : '保存配置' }}
              </button>
              <button
                type="button"
                @click="handleClearMemory"
                class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition"
              >
                清除记忆
              </button>
            </div>
            <p v-if="updateError" class="mt-4 text-sm text-red-400">{{ updateError }}</p>
          </form>
        </div>

        <!-- Set Context -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <h3 class="text-lg font-semibold text-white mb-4">设置上下文</h3>
          <form @submit.prevent="handleSetContext">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">上下文内容 (JSON)</label>
              <textarea
                v-model="contextForm"
                rows="4"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                placeholder='{"key": "value"}'
              ></textarea>
            </div>
            <button
              type="submit"
              :disabled="contextLoading"
              class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 transition"
            >
              {{ contextLoading ? '设置中...' : '设置上下文' }}
            </button>
            <p v-if="contextError" class="mt-4 text-sm text-red-400">{{ contextError }}</p>
          </form>
        </div>

        <!-- History -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white">对话历史</h3>
            <button
              @click="loadHistory"
              class="px-3 py-1 text-sm bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
            >
              刷新
            </button>
          </div>

          <div v-if="historyLoading" class="text-gray-400">加载中...</div>
          <div v-else-if="!history || history.total === 0" class="text-gray-400 text-center py-4">
            暂无历史记录
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="(msg, idx) in history.messages"
              :key="idx"
              class="bg-gray-700 rounded-lg p-3"
            >
              <pre class="text-gray-300 text-sm whitespace-pre-wrap">{{ JSON.stringify(msg, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import * as phase3Api from '@/api/phase3'
import type { AgentMemoryConfig, AgentHistory } from '@/types'

const router = useRouter()
const route = useRoute()
const agentId = route.params.id as string

const loading = ref(false)
const historyLoading = ref(false)
const updateLoading = ref(false)
const contextLoading = ref(false)
const updateError = ref('')
const contextError = ref('')
const memoryConfig = ref<AgentMemoryConfig | null>(null)
const history = ref<AgentHistory | null>(null)

const memoryForm = ref({
  memory_type: 'shortterm',
  max_context_tokens: 4096,
  context_window: 10,
  persist_context: true,
})

const contextForm = ref('{}')

onMounted(async () => {
  await loadMemory()
  await loadHistory()
})

const loadMemory = async () => {
  loading.value = true
  try {
    const res = await phase3Api.getAgentMemory(agentId)
    memoryConfig.value = res.data.data
    memoryForm.value = {
      memory_type: res.data.data.memory_type,
      max_context_tokens: res.data.data.max_context_tokens,
      context_window: res.data.data.context_window,
      persist_context: res.data.data.persist_context,
    }
  } catch {
    memoryConfig.value = null
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const res = await phase3Api.getAgentHistory(agentId)
    history.value = res.data.data
  } catch {
    history.value = null
  } finally {
    historyLoading.value = false
  }
}

const handleUpdateMemory = async () => {
  updateLoading.value = true
  updateError.value = ''
  try {
    await phase3Api.updateAgentMemory(agentId, {
      agent_id: agentId,
      ...memoryForm.value,
      context_items: memoryConfig.value?.context_items || 0,
    })
    await loadMemory()
  } catch {
    updateError.value = '更新失败'
  } finally {
    updateLoading.value = false
  }
}

const handleSetContext = async () => {
  contextLoading.value = true
  contextError.value = ''
  try {
    const context = JSON.parse(contextForm.value)
    await phase3Api.setAgentContext(agentId, { context })
    contextForm.value = '{}'
    await loadHistory()
  } catch {
    contextError.value = '设置失败，请检查 JSON 格式'
  } finally {
    contextLoading.value = false
  }
}

const handleClearMemory = async () => {
  if (!confirm('确定要清除所有记忆吗？')) return
  try {
    await phase3Api.clearAgentMemory(agentId)
    await loadHistory()
  } catch {}
}

const handleResetState = async () => {
  if (!confirm('确定要重置 Agent 状态吗？这将清除所有记忆并将状态设为离线。')) return
  try {
    await phase3Api.resetAgentState(agentId)
    router.push(`/agents/${agentId}`)
  } catch {}
}
</script>