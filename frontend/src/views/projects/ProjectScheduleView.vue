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
          <h2 class="text-2xl font-bold text-white">{{ projectStore.currentProject?.name }} — 定时调度</h2>
        </div>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建定时任务
        </button>
      </div>

      <div v-if="loading" class="text-gray-400 py-8 text-center">加载中...</div>
      <div v-else-if="!jobs.length" class="text-gray-400 text-center py-12">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p>暂无定时任务</p>
        <p class="text-sm mt-1">点击右上角按钮创建</p>
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
                  class="px-2 py-0.5 rounded text-xs font-medium"
                >
                  {{ job.enabled ? '启用' : '禁用' }}
                </span>
              </div>
              <div class="flex items-center gap-4 mt-2 text-sm text-gray-400">
                <span>Cron: <code class="text-purple-400">{{ job.cron_expression }}</code></span>
                <span v-if="job.next_run_at">下次: {{ formatDateTime(job.next_run_at) }}</span>
                <span v-if="job.last_run_at">上次: {{ formatDateTime(job.last_run_at) }}</span>
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
                @click="handleToggle(job)"
                class="px-3 py-1.5 text-sm bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
              >
                {{ job.enabled ? '暂停' : '启用' }}
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

      <!-- 创建弹窗 -->
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
                placeholder="例如：每天早上9点执行"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">选择任务</label>
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
                <option v-for="agent in agents" :key="agent.id" :value="agent.id">
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
              <p class="mt-1 text-xs text-gray-500">例如: "0 9 * * *" 表示每天9点执行</p>
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

      <!-- 执行记录弹窗 -->
      <div v-if="showRuns" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showRuns = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[600px] border border-gray-700 max-h-[80vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-white mb-4">执行记录</h3>
          <div v-if="runsLoading" class="text-gray-400">加载中...</div>
          <div v-else-if="!runs.length" class="text-gray-400 text-center py-4">暂无执行记录</div>
          <div v-else class="space-y-3">
            <div
              v-for="run in runs"
              :key="run.execution_id"
              class="bg-gray-700/50 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <span class="text-white text-sm font-mono">{{ run.execution_id?.slice(0, 8) }}...</span>
                <span :class="statusClass(run.status)" class="px-2 py-0.5 rounded text-xs">
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
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useProjectStore } from '@/stores/project'
import { useAgentStore } from '@/stores/agent'
import { listJobs, createJob, deleteJob, updateJob, getJobRuns, type SchedulerJob, type SchedulerJobCreate } from '@/api/scheduler'
import { listTasks } from '@/api/tasks'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string
const projectStore = useProjectStore()
const agentStore = useAgentStore()

const jobs = ref<SchedulerJob[]>([])
const tasks = ref<any[]>([])
const agents = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const createLoading = ref(false)
const createError = ref('')
const showRuns = ref(false)
const runs = ref<any[]>([])
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
    projectStore.fetchProject(projectId),
    fetchJobs(),
    fetchTasks(),
    agentStore.fetchAgents(),
  ])
  agents.value = agentStore.agents
  loading.value = false
})

const fetchJobs = async () => {
  try {
    const res = await listJobs()
    const allJobs = res.data.data.items || []
    // 筛选当前项目的任务（如果有 project_id 字段）
    jobs.value = allJobs.filter((j: any) => !j.project_id || j.project_id === projectId)
  } catch (e) {
    console.error('Failed to fetch jobs:', e)
  }
}

const fetchTasks = async () => {
  try {
    const res = await listTasks({ project_id: projectId })
    tasks.value = res.data.data.items || []
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  }
}

const handleCreate = async () => {
  createLoading.value = true
  createError.value = ''
  try {
    await createJob({ ...newJob.value, project_id: projectId } as any)
    showCreate.value = false
    newJob.value = { name: '', task_template_id: '', cron_expression: '0 9 * * *', agent_id: '', enabled: true }
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

const handleToggle = async (job: SchedulerJob) => {
  try {
    await updateJob(job.id, { enabled: !job.enabled })
    await fetchJobs()
  } catch (e) {
    console.error('Failed to toggle job:', e)
  }
}

const viewRuns = async (jobId: string) => {
  showRuns.value = true
  runsLoading.value = true
  try {
    const res = await getJobRuns(jobId)
    runs.value = res.data.data.items || []
  } catch (e) {
    console.error('Failed to fetch runs:', e)
    runs.value = []
  } finally {
    runsLoading.value = false
  }
}

const statusText = (status: string) => ({ success: '成功', failed: '失败', running: '执行中', pending: '等待中' }[status] || status)
const statusClass = (status: string) => ({
  'bg-green-500/20 text-green-400': status === 'success',
  'bg-red-500/20 text-red-400': status === 'failed',
  'bg-yellow-500/20 text-yellow-400': status === 'running',
  'bg-gray-500/20 text-gray-400': status === 'pending',
})

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
