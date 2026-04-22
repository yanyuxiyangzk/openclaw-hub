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
      <div v-else-if="!workflow" class="text-gray-400 text-center py-8">
        工作流不存在
      </div>
      <div v-else class="space-y-6">
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div class="flex items-start justify-between mb-6">
            <div>
              <h2 class="text-2xl font-bold text-white mb-2">{{ workflow.name }}</h2>
              <p class="text-gray-400 text-sm">{{ workflow.description || '暂无描述' }}</p>
            </div>
            <div class="flex gap-2">
              <button
                @click="executeWorkflow"
                :disabled="executing"
                class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
              >
                {{ executing ? '执行中...' : '执行工作流' }}
              </button>
              <button
                @click="deleteWorkflowById"
                class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30"
              >
                删除
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <label class="block text-gray-500 mb-1">ID</label>
              <p class="text-gray-300 font-mono">{{ workflow.id }}</p>
            </div>
            <div>
              <label class="block text-gray-500 mb-1">组织 ID</label>
              <p class="text-gray-300 font-mono">{{ workflow.org_id }}</p>
            </div>
            <div>
              <label class="block text-gray-500 mb-1">创建时间</label>
              <p class="text-gray-300">{{ formatDate(workflow.created_at) }}</p>
            </div>
            <div>
              <label class="block text-gray-500 mb-1">更新时间</label>
              <p class="text-gray-300">{{ formatDate(workflow.updated_at) }}</p>
            </div>
          </div>
        </div>

        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 class="text-lg font-semibold text-white mb-4">工作流步骤</h3>
          <div v-if="!workflow.steps?.length" class="text-gray-400 text-center py-4">
            暂无步骤
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(step, idx) in workflow.steps"
              :key="idx"
              class="bg-gray-700 rounded-lg p-4 border border-gray-600"
            >
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center text-purple-400 font-bold text-sm">
                  {{ idx + 1 }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-white font-medium">{{ step.name || step.step_id }}</span>
                    <span class="bg-gray-600 text-gray-300 px-2 py-0.5 rounded text-xs">{{ step.step_id }}</span>
                  </div>
                  <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span class="text-gray-500">任务模板: </span>
                      <span class="text-gray-300 font-mono">{{ step.task_template_id?.slice(0, 8) }}...</span>
                    </div>
                    <div>
                      <span class="text-gray-500">Agent: </span>
                      <span class="text-gray-300 font-mono">{{ step.agent_id?.slice(0, 8) }}...</span>
                    </div>
                  </div>
                  <div v-if="step.depends_on?.length" class="mt-2 text-sm">
                    <span class="text-gray-500">依赖: </span>
                    <span class="text-gray-300">{{ step.depends_on.join(', ') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Execution Results -->
        <div v-if="executionResults.length" class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 class="text-lg font-semibold text-white mb-4">执行结果</h3>
          <div class="space-y-3">
            <div
              v-for="result in executionResults"
              :key="result.id"
              class="bg-gray-700 rounded-lg p-3 flex items-center justify-between"
            >
              <div>
                <span class="text-gray-300">任务: {{ result.task_id?.slice(0, 8) }}...</span>
                <span class="text-gray-500 ml-4">Agent: {{ result.agent_id?.slice(0, 8) }}...</span>
              </div>
              <span :class="{
                'text-yellow-400': result.status === 'pending',
                'text-blue-400': result.status === 'running',
                'text-green-400': result.status === 'completed',
                'text-red-400': result.status === 'failed',
              }">{{ result.status }}</span>
            </div>
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
import { getWorkflow, executeWorkflow as executeWorkflowApi, deleteWorkflow } from '@/api/workflows'
import type { Workflow } from '@/api/workflows'
import type { Execution } from '@/api/executions'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const executing = ref(false)
const workflow = ref<Workflow | null>(null)
const executionResults = ref<Execution[]>([])

const loadWorkflow = async () => {
  try {
    const id = route.params.id as string
    const res = await getWorkflow(id)
    workflow.value = res.data.data || null
  } catch (err) {
    console.error('Failed to load workflow:', err)
  } finally {
    loading.value = false
  }
}

const executeWorkflow = async () => {
  if (!workflow.value) return
  executing.value = true
  try {
    const res = await executeWorkflowApi(workflow.value.id, {})
    executionResults.value = res.data.data?.items || []
  } catch (err) {
    console.error('Failed to execute workflow:', err)
  } finally {
    executing.value = false
  }
}

const deleteWorkflowById = async () => {
  if (!workflow.value) return
  if (!confirm('确定要删除这个工作流吗?')) return
  try {
    await deleteWorkflow(workflow.value.id)
    router.push('/workflows')
  } catch (err) {
    console.error('Failed to delete workflow:', err)
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
  loadWorkflow()
})
</script>
