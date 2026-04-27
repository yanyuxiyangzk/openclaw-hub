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
          <h2 class="text-2xl font-bold text-white">{{ projectStore.currentProject?.name }} — 数据概览</h2>
        </div>
        <select
          v-model="days"
          @change="fetchData"
          class="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option :value="7">近7天</option>
          <option :value="14">近14天</option>
          <option :value="30">近30天</option>
        </select>
      </div>

      <div v-if="loading" class="text-gray-400 py-8 text-center">加载中...</div>
      <div v-else>
        <!-- 统计卡片 -->
        <div class="grid grid-cols-4 gap-4 mb-8">
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-500 text-sm">项目任务</div>
            <div class="text-3xl font-bold text-primary-400 mt-1">{{ stats.task_count }}</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-500 text-sm">进行中</div>
            <div class="text-3xl font-bold text-blue-400 mt-1">{{ stats.in_progress_count }}</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-500 text-sm">已完成</div>
            <div class="text-3xl font-bold text-green-400 mt-1">{{ stats.completed_count }}</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-500 text-sm">执行次数</div>
            <div class="text-3xl font-bold text-purple-400 mt-1">{{ stats.execution_count }}</div>
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="grid grid-cols-2 gap-6 mb-8">
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <h3 class="font-semibold text-white mb-4">任务完成趋势（ {{ days }} 天）</h3>
            <div v-if="trend.length" class="flex items-end gap-2 h-40">
              <div
                v-for="item in trend"
                :key="item.date"
                class="flex-1 flex flex-col items-center"
              >
                <div
                  class="w-full bg-primary-500 rounded-t"
                  :style="{ height: `${(item.count / maxTrend) * 100}%` }"
                ></div>
                <div class="text-xs text-gray-500 mt-1">{{ item.date.slice(5) }}</div>
              </div>
            </div>
            <div v-else class="h-40 flex items-center justify-center text-gray-500">暂无数据</div>
          </div>

          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <h3 class="font-semibold text-white mb-4">最近活动</h3>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div
                v-for="a in recentActivities"
                :key="a.id"
                class="text-sm py-1 border-b border-gray-700 last:border-0"
              >
                <span class="text-white">{{ a.actor_name || '系统' }}</span>
                <span class="text-gray-500 ml-1">{{ actionText(a.action_type) }}</span>
                <span class="text-purple-400 ml-1">{{ a.entity_name || a.entity_type }}</span>
              </div>
              <div v-if="!recentActivities.length" class="text-gray-500 text-sm">暂无活动</div>
            </div>
          </div>
        </div>

        <!-- Agent 统计 -->
        <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <h3 class="font-semibold text-white mb-4">Agent 任务统计</h3>
          <div v-if="agentStats.length" class="space-y-3">
            <div v-for="as in agentStats" :key="as.agent_id" class="flex items-center gap-4">
              <div class="w-32 text-sm text-gray-400 truncate">{{ as.agent_name }}</div>
              <div class="flex-1 bg-gray-700 rounded-full h-2">
                <div
                  class="bg-purple-500 h-2 rounded-full"
                  :style="{ width: `${(as.count / maxAgentCount) * 100}%` }"
                ></div>
              </div>
              <div class="text-sm text-white w-12 text-right">{{ as.count }}</div>
            </div>
          </div>
          <div v-else class="text-gray-500 text-sm">暂无数据</div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useProjectStore } from '@/stores/project'
import { dashboardApi } from '@/api/dashboard'
import { activitiesApi } from '@/api/activities'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string
const projectStore = useProjectStore()

const loading = ref(false)
const days = ref(7)
const stats = ref({ task_count: 0, in_progress_count: 0, completed_count: 0, execution_count: 0 })
const trend = ref<{ date: string; count: number }[]>([])
const recentActivities = ref<any[]>([])
const agentStats = ref<{ agent_id: string; agent_name: string; count: number }[]>([])

const maxTrend = computed(() => Math.max(...trend.value.map(t => t.count), 1))
const maxAgentCount = computed(() => Math.max(...agentStats.value.map(a => a.count), 1))

onMounted(async () => {
  await projectStore.fetchProject(projectId)
  await fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const [statsRes, trendRes, activitiesRes] = await Promise.all([
      dashboardApi.getProjectStats(projectId),
      dashboardApi.getProjectTaskTrend(projectId, days.value),
      activitiesApi.list({ limit: 5, project_id: projectId }),
    ])
    stats.value = statsRes.data.data
    trend.value = trendRes.data.data || []
    recentActivities.value = activitiesRes.data.data.items || []
    // TODO: agent stats API
    agentStats.value = []
  } catch (e) {
    console.error('Failed to fetch dashboard data:', e)
  } finally {
    loading.value = false
  }
}

const actionText = (type: string) => ({
  created: '创建了', updated: '更新了', completed: '完成了', deleted: '删除了', assigned: '分配了'
}[type] || '操作了')
</script>
