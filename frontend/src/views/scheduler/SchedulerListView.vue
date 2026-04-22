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

      <div v-if="loading" class="text-gray-400 text-center py-8">加载中...</div>
      <div v-else-if="!jobs.length" class="text-gray-400 text-center py-8">
        暂无调度任务，点击上方按钮创建
      </div>
      <div v-else class="grid gap-4">
        <div
          v-for="job in jobs"
          :key="job.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700"
        >
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-3">
                <h3 class="text-lg font-semibold text-white">{{ job.name }}</h3>
                <span
                  :class="job.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'"
                  class="px-2 py-1 rounded text-xs font-medium"
                >
                  {{ job.enabled ? '启用' : '禁用' }}
                </span>
              </div>
              <p class="text-gray-400 text-sm mt-1">Cron: {{ job.cron_expression }}</p>
            </div>
            <div class="flex gap-2">
              <button
                @click="toggleJob(job)"
                class="text-xs px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
              >
                {{ job.enabled ? '暂停' : '启用' }}
              </button>
              <button
                @click="viewRuns(job.id)"
                class="text-xs px-3 py-1 bg-blue-500/20 text-blue-400 rounded hover:bg-blue-500/30"
              >
                查看执行
              </button>
              <button
                @click="deleteJob(job.id)"
                class="text-xs px-3 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30"
              >
                删除
              </button>
            </div>
          </div>
          <div class="flex items-center gap-6 mt-3 text-sm text-gray-500">
            <span>Agent: {{ job.agent_id.substring(0, 8) }}...</span>
            <span>任务模板: {{ job.task_template_id.substring(0, 8) }}...</span>
            <span v-if="job.last_run_at">上次运行: {{ formatDate(job.last_run_at) }}</span>
            <span v-if="job.next_run_at">下次运行: {{ formatDate(job.next_run_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Runs Modal -->
      <div v-if="showRuns" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showRuns = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[600px] border border-gray-700 max-h-[80vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-white mb-4">执行记录</h3>
          <div v-if="runsLoading" class="text-gray-400">加载中...</div>
          <div v-else-if="!runs.length" class="text-gray-500 text-center py-4">暂无执行记录</div>
          <div v-else class="space-y-2">
            <div
              v-for="run in runs"
              :key="run.execution_id"
              class="flex items-center justify-between p-3 bg-gray-700 rounded"
            >
              <span class="text-gray-300 text-sm font-mono">{{ run.execution_id.substring(0, 12) }}...</span>
              <ExecutionStatus :status="run.status" />
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

      <!-- Create Modal -->
      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-[500px] border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">创建调度任务</h3>
          <SchedulerConfig
            :agents="agents"
            :show-save="true"
            :show-test="true"
            :saving="createLoading"
            @save="handleCreate"
          />
          <button
            @click="showCreate = false"
            class="mt-4 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import SchedulerConfig from '@/components/scheduler/SchedulerConfig.vue'
import ExecutionStatus from '@/components/executions/ExecutionStatus.vue'
import { listJobs, createJob, deleteJob as deleteJobApi, getJobRuns } from '@/api/scheduler'
import { listAgents } from '@/api/agents'
import type { SchedulerJob, SchedulerJobCreate, JobRun } from '@/api/scheduler'
import type { Agent } from '@/types'

const jobs = ref<SchedulerJob[]>([])
const agents = ref<Agent[]>([])
const loading = ref(false)
const createLoading = ref(false)
const showCreate = ref(false)
const showRuns = ref(false)
const runs = ref<JobRun[]>([])
const runsLoading = ref(false)

const loadJobs = async () => {
  loading.value = true
  try {
    const res = await listJobs()
    if (res.data.code === 0) {
      jobs.value = res.data.data.items
    }
  } catch (e) {
    console.error('Failed to load jobs:', e)
  } finally {
    loading.value = false
  }
}

const loadAgents = async () => {
  try {
    const res = await listAgents()
    if (res.data.code === 0) {
      agents.value = res.data.data || []
    }
  } catch (e) {
    console.error('Failed to load agents:', e)
  }
}

const handleCreate = async (config: any) => {
  createLoading.value = true
  try {
    await createJob(config as SchedulerJobCreate)
    showCreate.value = false
    await loadJobs()
  } catch (e) {
    console.error('Failed to create job:', e)
  } finally {
    createLoading.value = false
  }
}

const toggleJob = async (job: SchedulerJob) => {
  // Toggle would require update API
  console.log('Toggle job:', job.id)
}

const viewRuns = async (jobId: string) => {
  runsLoading.value = true
  showRuns.value = true
  try {
    const res = await getJobRuns(jobId)
    if (res.data.code === 0) {
      runs.value = res.data.data.items
    }
  } catch (e) {
    console.error('Failed to load runs:', e)
  } finally {
    runsLoading.value = false
  }
}

const deleteJob = async (jobId: string) => {
  if (!confirm('确定要删除这个调度任务吗？')) return
  try {
    await deleteJobApi(jobId)
    await loadJobs()
  } catch (e) {
    console.error('Failed to delete job:', e)
  }
}

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadJobs()
  loadAgents()
})
</script>