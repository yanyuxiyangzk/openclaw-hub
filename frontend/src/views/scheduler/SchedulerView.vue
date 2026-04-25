<template>
  <AppLayout>
    <div class="max-w-5xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">定时任务调度</h2>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建定时任务
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="jobs.length === 0" class="text-gray-400 text-center py-8">
        暂无定时任务，点击上方按钮创建
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="job in jobs"
          :key="job.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <h3 class="text-lg font-semibold text-white">{{ job.name }}</h3>
                <span
                  :class="job.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'"
                  class="px-2 py-1 rounded text-xs font-medium"
                >
                  {{ job.enabled ? '启用' : '禁用' }}
                </span>
              </div>
              <div class="flex items-center gap-4 mt-2 text-sm text-gray-400">
                <span>Cron: {{ job.cron_expression }}</span>
                <span v-if="job.next_run_at">下次执行: {{ formatDateTime(job.next_run_at) }}</span>
                <span v-if="job.last_run_at">上次执行: {{ formatDateTime(job.last_run_at) }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="viewRuns(job.id)"
                class="px-3 py-1.5 text-sm bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
              >
                执行记录
              </button>
              <button
                @click="handleDelete(job.id)"
                class="px-3 py-1.5 text-sm bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[520px] border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">创建定时任务</h3>
          <form @submit.prevent="handleCreate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">任务名称</label>
              <input
                v-model="newJob.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">选择任务模板</label>
              <select
                v-model="newJob.task_template_id"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="" disabled>选择任务</option>
                <option v-for="task in tasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">选择 Agent</label>
              <select
                v-model="newJob.agent_id"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="" disabled>选择 Agent</option>
                <option v-for="agent in agentStore.agents" :key="agent.id" :value="agent.id">
                  {{ agent.name }} ({{ agent.status }})
                </option>
              </select>
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">Cron 表达式</label>
              <input
                v-model="newJob.cron_expression"
                type="text"
                placeholder="* * * * * (分 时 日 月 周)"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <p class="mt-1 text-xs text-gray-500">
                例如: "0 9 * * *" 表示每天9点执行
              </p>
            </div>
            <div class="mb-4">
              <label class="flex items-center gap-2 text-gray-400 cursor-pointer">
                <input
                  v-model="newJob.enabled"
                  type="checkbox"
                  class="w-4 h-4 rounded bg-gray-700 border-gray-600 text-purple-500 focus:ring-purple-500"
                />
                <span class="text-sm">创建后立即启用</span>
              </label>
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

      <div v-if="showRuns" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showRuns = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[600px] border border-gray-700 max-h-[80vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-white mb-4">执行记录</h3>
          <div v-if="runsLoading" class="text-gray-400">加载中...</div>
          <div v-else-if="runs.length === 0" class="text-gray-400 text-center py-4">
            暂无执行记录
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="run in runs"
              :key="run.execution_id"
              class="bg-gray-700/50 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <span class="text-white text-sm font-mono">{{ run.execution_id.slice(0, 8) }}...</span>
                <span
                  :class="{
                    'bg-green-500/20 text-green-400': run.status === 'success',
                    'bg-red-500/20 text-red-400': run.status === 'failed',
                    'bg-yellow-500/20 text-yellow-400': run.status === 'running',
                    'bg-gray-500/20 text-gray-400': run.status === 'pending',
                  }"
                  class="px-2 py-0.5 rounded text-xs"
                >
                  {{ statusText(run.status) }}
                </span>
              </div>
              <div class="flex items-center gap-4 mt-1 text-xs text-gray-400">
                <span v-if="run.started_at">开始: {{ formatDateTime(run.started_at) }}</span>
                <span v-if="run.completed_at">完成: {{ formatDateTime(run.completed_at) }}</span>
              </div>
            </div>
          </div>
          <div class="mt-4 flex justify-end">
            <button
              @click="showRuns = false"
              class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAgentStore } from '@/stores/agent'
import { listJobs, createJob, deleteJob, getJobRuns, type SchedulerJob, type SchedulerJobCreate } from '@/api/scheduler'
import { listTasks } from '@/api/tasks'
import type { Task } from '@/api/tasks'

const agentStore = useAgentStore()

const jobs = ref<SchedulerJob[]>([])
const tasks = ref<Task[]>([])
const loading = ref(false)
const showCreate = ref(false)
const createLoading = ref(false)
const createError = ref('')
const showRuns = ref(false)
const runs = ref<Array<{
  execution_id: string
  status: string
  started_at?: string
  completed_at?: string
  created_at: string
}>>([])
const runsLoading = ref(false)

const newJob = ref<SchedulerJobCreate>({
  name: '',
  task_template_id: '',
  cron_expression: '0 9 * * *',
  agent_id: '',
  enabled: true,
})

onMounted(async () => {
  loading.value = true
  await Promise.all([
    fetchJobs(),
    agentStore.fetchAgents(),
    fetchTasks(),
  ])
  loading.value = false
})

const fetchJobs = async () => {
  try {
    const res = await listJobs()
    jobs.value = res.data.data.items
  } catch (e) {
    console.error('Failed to fetch jobs:', e)
  }
}

const fetchTasks = async () => {
  try {
    const res = await listTasks()
    tasks.value = res.data.data.items
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

const handleCreate = async () => {
  createLoading.value = true
  createError.value = ''
  try {
    await createJob(newJob.value)
    showCreate.value = false
    newJob.value = {
      name: '',
      task_template_id: '',
      cron_expression: '0 9 * * *',
      agent_id: '',
      enabled: true,
    }
    await fetchJobs()
  } catch (e: any) {
    createError.value = e?.response?.data?.message || '创建失败'
  } finally {
    createLoading.value = false
  }
}

const handleDelete = async (id: string) => {
  if (!confirm('确定要删除这个定时任务吗？')) return
  try {
    await deleteJob(id)
    await fetchJobs()
  } catch (e) {
    console.error('Failed to delete job:', e)
  }
}

const viewRuns = async (jobId: string) => {
  showRuns.value = true
  runsLoading.value = true
  try {
    const res = await getJobRuns(jobId)
    runs.value = res.data.data.items
  } catch (e) {
    console.error('Failed to fetch runs:', e)
    runs.value = []
  } finally {
    runsLoading.value = false
  }
}

const statusText = (status: string) => {
  const map: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '执行中',
    pending: '等待中',
  }
  return map[status] || status
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
