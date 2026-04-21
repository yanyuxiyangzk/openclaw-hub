<template>
  <AppLayout>
    <div class="max-w-6xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push(`/agents/${agentId}`)" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">Agent 指标</h2>
        </div>
        <div class="flex gap-2">
          <select
            v-model="selectedDays"
            @change="loadMetrics"
            class="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option :value="7">最近 7 天</option>
            <option :value="14">最近 14 天</option>
            <option :value="30">最近 30 天</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <template v-else>
        <!-- Performance Overview -->
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-400 text-sm mb-1">任务总数</div>
            <div class="text-2xl font-bold text-white">{{ performance?.total_tasks || 0 }}</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-400 text-sm mb-1">成功率</div>
            <div class="text-2xl font-bold text-green-400">{{ performance?.success_rate || 0 }}%</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-400 text-sm mb-1">平均响应时间</div>
            <div class="text-2xl font-bold text-white">{{ performance?.avg_response_time_ms || 0 }} ms</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div class="text-gray-400 text-sm mb-1">Token 使用</div>
            <div class="text-2xl font-bold text-white">{{ formatNumber(performance?.avg_tokens_per_task || 0) }}</div>
          </div>
        </div>

        <!-- Task Counts -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <h3 class="text-lg font-semibold text-white mb-4">任务统计</h3>
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center">
              <div class="text-3xl font-bold text-white">{{ taskCounts?.total_tasks || 0 }}</div>
              <div class="text-gray-400 text-sm">总任务</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-green-400">{{ taskCounts?.completed_tasks || 0 }}</div>
              <div class="text-gray-400 text-sm">已完成</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-red-400">{{ taskCounts?.failed_tasks || 0 }}</div>
              <div class="text-gray-400 text-sm">失败</div>
            </div>
          </div>
        </div>

        <!-- Daily Metrics Chart -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <h3 class="text-lg font-semibold text-white mb-4">每日指标</h3>
          <div v-if="metrics.length === 0" class="text-gray-400 text-center py-8">
            暂无数据
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="text-gray-400 text-sm border-b border-gray-700">
                  <th class="text-left py-2 px-3">日期</th>
                  <th class="text-right py-2 px-3">完成任务</th>
                  <th class="text-right py-2 px-3">失败任务</th>
                  <th class="text-right py-2 px-3">平均响应时间</th>
                  <th class="text-right py-2 px-3">Token 使用</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in metrics" :key="m.id" class="border-b border-gray-700/50 text-white">
                  <td class="py-2 px-3">{{ m.date }}</td>
                  <td class="text-right py-2 px-3 text-green-400">{{ m.tasks_completed }}</td>
                  <td class="text-right py-2 px-3 text-red-400">{{ m.tasks_failed }}</td>
                  <td class="text-right py-2 px-3">{{ m.avg_response_time_ms }} ms</td>
                  <td class="text-right py-2 px-3">{{ formatNumber(m.token_usage) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Health Details -->
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 class="text-lg font-semibold text-white mb-4">健康状态详情</h3>
          <div v-if="healthDetail" class="grid grid-cols-2 gap-4">
            <div class="flex items-center justify-between bg-gray-700 rounded-lg p-4">
              <span class="text-gray-400">状态</span>
              <span :class="healthDetail.healthy ? 'text-green-400' : 'text-red-400'" class="font-medium">
                {{ healthDetail.healthy ? '健康' : '异常' }}
              </span>
            </div>
            <div class="flex items-center justify-between bg-gray-700 rounded-lg p-4">
              <span class="text-gray-400">Agent 状态</span>
              <span class="text-white font-medium">{{ healthDetail.status }}</span>
            </div>
            <div class="flex items-center justify-between bg-gray-700 rounded-lg p-4">
              <span class="text-gray-400">CPU 使用</span>
              <span class="text-white font-medium">{{ healthDetail.cpu_percent?.toFixed(1) || '-' }}%</span>
            </div>
            <div class="flex items-center justify-between bg-gray-700 rounded-lg p-4">
              <span class="text-gray-400">内存使用</span>
              <span class="text-white font-medium">{{ healthDetail.memory_mb?.toFixed(1) || '-' }} MB</span>
            </div>
            <div class="flex items-center justify-between bg-gray-700 rounded-lg p-4">
              <span class="text-gray-400">运行时长</span>
              <span class="text-white font-medium">{{ formatUptime(healthDetail.uptime_seconds) }}</span>
            </div>
            <div class="flex items-center justify-between bg-gray-700 rounded-lg p-4">
              <span class="text-gray-400">今日错误数</span>
              <span :class="healthDetail.error_count_today > 0 ? 'text-red-400' : 'text-green-400'" class="font-medium">
                {{ healthDetail.error_count_today }}
              </span>
            </div>
          </div>
          <div v-else class="text-gray-400 text-center py-4">
            暂无健康数据
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
import type { AgentMetric, AgentTaskCount, AgentPerformance, AgentHealthDetail } from '@/types'

const router = useRouter()
const route = useRoute()
const agentId = route.params.id as string

const loading = ref(false)
const selectedDays = ref(7)
const metrics = ref<AgentMetric[]>([])
const taskCounts = ref<AgentTaskCount | null>(null)
const performance = ref<AgentPerformance | null>(null)
const healthDetail = ref<AgentHealthDetail | null>(null)

onMounted(async () => {
  await loadMetrics()
})

const loadMetrics = async () => {
  loading.value = true
  try {
    const [metricsRes, countsRes, perfRes, healthRes] = await Promise.all([
      phase3Api.getAgentMetrics(agentId, selectedDays.value),
      phase3Api.getAgentTaskCounts(agentId),
      phase3Api.getAgentPerformance(agentId, selectedDays.value),
      phase3Api.getAgentHealthDetail(agentId),
    ])
    metrics.value = metricsRes.data.data
    taskCounts.value = countsRes.data.data
    performance.value = perfRes.data.data
    healthDetail.value = healthRes.data.data
  } catch {
    metrics.value = []
  } finally {
    loading.value = false
  }
}

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatUptime = (seconds: number | null) => {
  if (!seconds) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}h ${m}m`
}
</script>