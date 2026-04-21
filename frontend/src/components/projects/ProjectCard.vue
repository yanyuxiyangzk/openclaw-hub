<template>
  <div
    class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-start justify-between">
      <div>
        <h3 class="text-lg font-semibold text-white">{{ project.name }}</h3>
        <p class="text-gray-400 text-sm mt-1">{{ project.description || '暂无描述' }}</p>
      </div>
      <span
        :class="{
          'bg-green-500/20 text-green-400': project.status === 'active',
          'bg-yellow-500/20 text-yellow-400': project.status === 'archived',
          'bg-red-500/20 text-red-400': project.status === 'deleted'
        }"
        class="px-2 py-1 rounded text-xs font-medium"
      >
        {{ statusText(project.status) }}
      </span>
    </div>
    <div class="flex items-center gap-4 mt-3">
      <span v-if="memberCount !== undefined" class="text-gray-500 text-xs">
        {{ memberCount }} 位成员
      </span>
      <span v-if="agentCount !== undefined" class="text-gray-500 text-xs">
        {{ agentCount }} 个 Agent
      </span>
      <span class="text-gray-500 text-xs">
        创建于 {{ formatDate(project.created_at) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Project } from '@/types'

defineProps<{
  project: Project
  memberCount?: number
  agentCount?: number
}>()

defineEmits<{
  click: []
}>()

const statusText = (status: string) => {
  const map: Record<string, string> = {
    active: '进行中',
    archived: '已归档',
    deleted: '已删除',
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>