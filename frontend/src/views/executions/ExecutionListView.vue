<template>
  <AppLayout>
    <div class="max-w-6xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">执行记录</h2>
        <div class="flex gap-2">
          <select
            v-model="statusFilter"
            class="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">全部状态</option>
            <option value="pending">等待中</option>
            <option value="running">运行中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="!executions.length" class="text-gray-400 text-center py-8">
        暂无执行记录
      </div>
      <div v-else class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-700 text-gray-400 text-sm">
            <tr>
              <th class="px-4 py-3 text-left">ID</th>
              <th class="px-4 py-3 text-left">任务</th>
              <th class="px-4 py-3 text-left">Agent</th>
              <th class="px-4 py-3 text-left">状态</th>
              <th class="px-4 py-3 text-left">开始时间</th>
              <th class="px-4 py-3 text-left">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr
              v-for="execution in executions"
              :key="execution.id"
              class="hover:bg-gray-700/50 cursor-pointer"
              @click="router.push(`/executions/${execution.id}`)"
            >
              <td class="px-4 py-3 text-gray-400 text-sm font-mono">{{ execution.id.slice(0, 8) }}</td>
              <td class="px-4 py-3 text-white">{{ execution.task_id.slice(0, 8) }}...</td>
              <td class="px-4 py-3 text-gray-300">{{ execution.agent_id.slice(0, 8) }}...</td>
              <td class="px-4 py-3">
                <ExecutionStatus :status="execution.status" />
              </td>
              <td class="px-4 py-3 text-gray-400 text-sm">
                {{ execution.started_at ? formatDate(execution.started_at) : '-' }}
              </td>
              <td class="px-4 py-3" @click.stop>
                <div class="flex gap-2">
                  <button
                    v-if="execution.status === 'pending' || execution.status === 'running'"
                    @click="handleCancel(execution.id)"
                    class="text-xs text-red-400 hover:text-red-300"
                  >
                    取消
                  </button>
                  <button
                    v-if="execution.status === 'failed' || execution.status === 'cancelled'"
                    @click="handleRetry(execution.id)"
                    class="text-xs text-purple-400 hover:text-purple-300"
                  >
                    重试
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import ExecutionStatus from '@/components/executions/ExecutionStatus.vue'
import { listExecutions } from '@/api/executions'
import type { Execution } from '@/api/executions'

const router = useRouter()
const loading = ref(true)
const executions = ref<Execution[]>([])
const statusFilter = ref('')

const loadExecutions = async () => {
  try {
    const res = await listExecutions(statusFilter.value || undefined)
    executions.value = res.data.data?.items || []
  } catch (err) {
    console.error('Failed to load executions:', err)
  } finally {
    loading.value = false
  }
}

watch(statusFilter, () => {
  loadExecutions()
})

const handleCancel = async (id: string) => {
  try {
    await import('@/api/executions').then(m => m.cancelExecution(id))
    await loadExecutions()
  } catch (err) {
    console.error('Failed to cancel execution:', err)
  }
}

const handleRetry = async (id: string) => {
  try {
    await import('@/api/executions').then(m => m.retryExecution(id))
    await loadExecutions()
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
  loadExecutions()
})
</script>
