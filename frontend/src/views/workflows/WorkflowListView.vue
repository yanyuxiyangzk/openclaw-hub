<template>
  <AppLayout>
    <div class="max-w-6xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">工作流</h2>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建工作流
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="!workflows.length" class="text-gray-400 text-center py-8">
        暂无工作流，点击上方按钮创建
      </div>
      <div v-else class="grid gap-4">
        <div
          v-for="workflow in workflows"
          :key="workflow.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition cursor-pointer"
          @click="router.push(`/workflows/${workflow.id}`)"
        >
          <div class="flex items-start justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white">{{ workflow.name }}</h3>
              <p class="text-gray-400 text-sm mt-1">{{ workflow.description || '暂无描述' }}</p>
            </div>
            <span class="bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs font-medium">
              {{ workflow.steps?.length || 0 }} 步骤
            </span>
          </div>
          <div class="flex items-center gap-4 mt-3">
            <span class="text-gray-500 text-xs">ID: {{ workflow.id.slice(0, 8) }}...</span>
            <span class="text-gray-500 text-xs">创建于 {{ formatDate(workflow.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Create Modal -->
      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[700px] border border-gray-700 max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-white mb-4">创建工作流</h3>
          <form @submit.prevent="handleCreate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">工作流名称</label>
              <input
                v-model="newWorkflow.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">描述</label>
              <textarea
                v-model="newWorkflow.description"
                rows="2"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              ></textarea>
            </div>

            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">步骤</label>
              <div class="space-y-3">
                <div
                  v-for="(step, idx) in newWorkflow.steps"
                  :key="idx"
                  class="bg-gray-700 rounded-lg p-3 border border-gray-600"
                >
                  <div class="flex items-start gap-3">
                    <div class="flex-1 space-y-2">
                      <div class="flex gap-2">
                        <input
                          v-model="step.step_id"
                          type="text"
                          placeholder="步骤ID"
                          class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                        <input
                          v-model="step.name"
                          type="text"
                          placeholder="步骤名称"
                          class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </div>
                      <div class="flex gap-2">
                        <input
                          v-model="step.task_template_id"
                          type="text"
                          placeholder="任务模板ID"
                          class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                        <input
                          v-model="step.agent_id"
                          type="text"
                          placeholder="Agent ID"
                          class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                        />
                      </div>
                    </div>
                    <button
                      type="button"
                      @click="removeStep(idx)"
                      class="text-red-400 hover:text-red-300 p-1"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
              <button
                type="button"
                @click="addStep"
                class="mt-2 text-sm text-purple-400 hover:text-purple-300"
              >
                + 添加步骤
              </button>
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
import AppLayout from '@/components/layout/AppLayout.vue'
import { listWorkflows, createWorkflow } from '@/api/workflows'
import type { Workflow, WorkflowCreate } from '@/api/workflows'

const router = useRouter()
const loading = ref(true)
const workflows = ref<Workflow[]>([])
const showCreate = ref(false)
const createLoading = ref(false)
const createError = ref('')

const newWorkflow = ref<WorkflowCreate>({
  name: '',
  description: '',
  steps: [],
})

const loadWorkflows = async () => {
  try {
    const res = await listWorkflows()
    workflows.value = res.data.data?.items || []
  } catch (err) {
    console.error('Failed to load workflows:', err)
  } finally {
    loading.value = false
  }
}

const addStep = () => {
  newWorkflow.value.steps.push({
    step_id: `step_${newWorkflow.value.steps.length + 1}`,
    name: '',
    task_template_id: '',
    agent_id: '',
    depends_on: [],
  })
}

const removeStep = (idx: number) => {
  newWorkflow.value.steps.splice(idx, 1)
}

const handleCreate = async () => {
  createLoading.value = true
  createError.value = ''
  try {
    await createWorkflow(newWorkflow.value)
    showCreate.value = false
    newWorkflow.value = { name: '', description: '', steps: [] }
    await loadWorkflows()
  } catch (err: any) {
    createError.value = err.message || '创建失败'
  } finally {
    createLoading.value = false
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
  loadWorkflows()
})
</script>
