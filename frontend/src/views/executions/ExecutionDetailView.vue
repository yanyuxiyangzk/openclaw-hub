<template>
  <AppLayout>
    <div class="max-w-4xl">
      <button
        @click="router.back()"
        class="mb-4 text-gray-400 hover:text-white flex items-center gap-1"
      >
        ← 返回
      </button>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="!execution" class="text-gray-400 text-center py-8">
        执行记录不存在
      </div>
      <div v-else class="space-y-6">
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div class="flex items-start justify-between mb-6">
            <div>
              <h2 class="text-2xl font-bold text-white mb-2">执行详情</h2>
              <p class="text-gray-400 text-sm font-mono">{{ execution.id }}</p>
            </div>
            <ExecutionStatus :status="execution.status" />
          </div>

          <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label class="block text-gray-500 text-sm mb-1">任务 ID</label>
              <p class="text-white font-mono text-sm">{{ execution.task_id }}</p>
            </div>
            <div>
              <label class="block text-gray-500 text-sm mb-1">Agent ID</label>
              <p class="text-white font-mono text-sm">{{ execution.agent_id }}</p>
            </div>
            <div>
              <label class="block text-gray-500 text-sm mb-1">创建时间</label>
              <p class="text-white text-sm">{{ formatDate(execution.created_at) }}</p>
            </div>
            <div>
              <label class="block text-gray-500 text-sm mb-1">开始时间</label>
              <p class="text-white text-sm">{{ execution.started_at ? formatDate(execution.started_at) : '-' }}</p>
            </div>
            <div v-if="execution.completed_at">
              <label class="block text-gray-500 text-sm mb-1">完成时间</label>
              <p class="text-white text-sm">{{ formatDate(execution.completed_at) }}</p>
            </div>
          </div>

          <div v-if="execution.error_message" class="mb-6">
            <label class="block text-gray-500 text-sm mb-2">错误信息</label>
            <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm font-mono">
              {{ execution.error_message }}
            </div>
          </div>

          <div class="flex gap-3">
            <button
              v-if="execution.status === 'pending' || execution.status === 'running'"
              @click="handleCancel"
              class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              取消执行
            </button>
            <button
              v-if="execution.status === 'failed' || execution.status === 'cancelled'"
              @click="handleRetry"
              class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
            >
              重试执行
            </button>
          </div>
        </div>

        <div v-if="execution.output_data" class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 class="text-lg font-semibold text-white mb-4">输出数据</h3>
          <pre class="bg-gray-900 rounded-lg p-4 text-gray-300 text-sm font-mono overflow-x-auto">{{ JSON.stringify(execution.output_data, null, 2) }}</pre>
        </div>

        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 class="text-lg font-semibold text-white mb-4">输入数据</h3>
          <pre class="bg-gray-900 rounded-lg p-4 text-gray-300 text-sm font-mono overflow-x-auto">{{ JSON.stringify(execution.input_data || {}, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import ExecutionStatus from '@/components/executions/ExecutionStatus.vue'
import { getExecution, cancelExecution, retryExecution } from '@/api/executions'
import type { Execution } from '@/api/executions'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const execution = ref<Execution | null>(null)

const loadExecution = async () => {
  try {
    const id = route.params.id as string
    const res = await getExecution(id)
    execution.value = res.data.data || null
  } catch (err) {
    console.error('Failed to load execution:', err)
  } finally {
    loading.value = false
  }
}

const handleCancel = async () => {
  if (!execution.value) return
  try {
    await cancelExecution(execution.value.id)
    await loadExecution()
  } catch (err) {
    console.error('Failed to cancel execution:', err)
  }
}

const handleRetry = async () => {
  if (!execution.value) return
  try {
    await retryExecution(execution.value.id)
    await loadExecution()
  } catch (err) {
    console.error('Failed to retry execution:', err)
  }
}

const formatDate = (date: string) => {
  try {
    return new Date(date).toLocaleString()
  } catch {
    return date
  }
}

onMounted(() => {
  loadExecution()
})
</script>
