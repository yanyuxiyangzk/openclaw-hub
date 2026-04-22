<template>
  <AppLayout>
    <div class="max-w-6xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">调度任务</h2>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建调度任务
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="!jobs.length" class="text-gray-400 text-center py-8">
        暂无调度任务，点击上方按钮创建
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="job in jobs"
          :key="job.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-white">{{ job.name }}</h3>
                <span
                  :class="job.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'"
                  class="px-2 py-0.5 rounded text-xs font-medium"
                >
                  {{ job.enabled ? '启用' : '禁用' }}
                </span>
              </div>
              <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">Cron: </span>
                  <span class="text-gray-300 font-mono">{{ job.cron_expression }}</span>
                </div>
                <div>
                  <span class="text-gray-500">下次运行: </span>
                  <span class="text-gray-300">{{ job.next_run_at ? formatDate(job.next_run_at) : '-' }}</span>
                </div>
                <div>
                  <span class="text-gray-500">上次运行: </span>
                  <span class="text-gray-300">{{ job.last_run_at ? formatDate(job.last_run_at) : '从未运行' }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2 ml-4">
              <button
                @click="toggleJob(job)"
                class="text-xs px-3 py-1 rounded"
                :class="job.enabled ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'"
              >
                {{ job.enabled ? '暂停' : '启用' }}
              </button>
              <button
                @click="viewRuns(job.id)"
                class="text-xs px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
              >
                执行记录
              </button>
              <button
                @click="deleteJobById(job.id)"
                class="text-xs px-3 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Modal -->
      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[500px] border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">创建调度任务</h3>
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
              <label class="block text-gray-400 mb-2 text-sm">Cron 表达式</label>
              <input
                v-model="newJob.cron_expression"
                type="text"
                placeholder="* * * * *"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <p class="text-gray-500 text-xs mt-1">格式: 分 时 日 月 周 (例: 0 9 * * * = 每天9点)</p>
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">任务模板 ID</label>
              <input
                v-model="newJob.task_template_id"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">Agent ID</label>
              <input
                v-model="newJob.agent_id"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
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

      <!-- Runs Modal -->
      <div v-if="showRuns" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showRuns = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[600px] border border-gray-700 max-h-[80vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-white mb-4">执行记录</h3>
          <div v-if="!runs.length" class="text-gray-400 text-center py-4">暂无执行记录</div>
          <div v-else class="space-y-2">
            <div v-for="run in runs" :key="run.execution_id" class="bg-gray-700 rounded p-3 flex items-center justify-between">
              <span class="text-gray-300 text-sm font-mono">{{ run.execution_id.slice(0, 8) }}...</span>
              <span :class="{
                'text-yellow-400': run.status === 'pending',
                'text-blue-400': run.status === 'running',
                'text-green-400': run.status === 'completed',
                'text-red-400': run.status === 'failed',
              }">{{ run.status }}</span>
              <span class="text-gray-500 text-xs">{{ formatDate(run.created_at) }}</span>
            </div>
          </div>
          <button
            @click="showRuns = false"
            class="mt-4 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { listJobs, createJob, deleteJob, updateJob, getJobRuns } from '@/api/scheduler'
import type { SchedulerJob, SchedulerJobCreate } from '@/api/scheduler'

const loading = ref(true)
const jobs = ref<SchedulerJob[]>([])
const showCreate = ref(false)
const showRuns = ref(false)
const runs = ref<any[]>([])
const createLoading = ref(false)
const createError = ref('')
const currentJobId = ref('')

const newJob = ref<SchedulerJobCreate>({
  name: '',
  cron_expression: '',
  task_template_id: '',
  agent_id: '',
  enabled: true,
})

const loadJobs = async () => {
  try {
    const res = await listJobs()
    jobs.value = res.data.data?.items || []
  } catch (err) {
    console.error('Failed to load jobs:', err)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  createLoading.value = true
  createError.value = ''
  try {
    await createJob(newJob.value)
    showCreate.value = false
    newJob.value = { name: '', cron_expression: '', task_template_id: '', agent_id: '', enabled: true }
    await loadJobs()
  } catch (err: any) {
    createError.value = err.message || '创建失败'
  } finally {
    createLoading.value = false
  }
}

const toggleJob = async (job: SchedulerJob) => {
  try {
    await updateJob(job.id, { enabled: !job.enabled })
    await loadJobs()
  } catch (err) {
    console.error('Failed to toggle job:', err)
  }
}

const deleteJobById = async (id: string) => {
  if (!confirm('确定要删除这个调度任务吗?')) return
  try {
    await deleteJob(id)
    await loadJobs()
  } catch (err) {
    console.error('Failed to delete job:', err)
  }
}

const viewRuns = async (id: string) => {
  currentJobId.value = id
  try {
    const res = await getJobRuns(id)
    runs.value = res.data.data?.items || []
    showRuns.value = true
  } catch (err) {
    console.error('Failed to load runs:', err)
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
  loadJobs()
})
</script>
