<template>
  <div
    class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-start justify-between">
      <div>
        <h3 class="text-lg font-semibold text-white">{{ agent.name }}</h3>
        <p class="text-gray-400 text-sm mt-1">{{ agent.description || '暂无描述' }}</p>
      </div>
      <span
        :class="{
          'bg-green-500/20 text-green-400': agent.status === 'online',
          'bg-yellow-500/20 text-yellow-400': agent.status === 'busy',
          'bg-red-500/20 text-red-400': agent.status === 'error',
          'bg-gray-500/20 text-gray-400': agent.status === 'offline',
        }"
        class="px-2 py-1 rounded text-xs font-medium"
      >
        {{ statusText(agent.status) }}
      </span>
    </div>
    <div class="flex items-center gap-4 mt-3">
      <span class="text-gray-500 text-xs">类型: {{ agent.agent_type }}</span>
      <span v-if="projectCount !== undefined" class="text-gray-500 text-xs">
        {{ projectCount }} 个项目
      </span>
      <span class="text-gray-500 text-xs">
        创建于 {{ formatDate(agent.created_at) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Agent } from '@/types'

defineProps<{
  agent: Agent
  projectCount?: number
}>()

defineEmits<{
  click: []
}>()

const statusText = (status: string) => {
  const map: Record<string, string> = {
    online: '在线',
    busy: '忙碌',
    error: '错误',
    offline: '离线',
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>