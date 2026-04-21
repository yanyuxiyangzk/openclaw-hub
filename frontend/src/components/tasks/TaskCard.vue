<template>
  <div
    class="task-card bg-white rounded-lg shadow-sm border border-gray-200 p-3 cursor-pointer hover:shadow-md transition-shadow"
    :class="priorityClass"
  >
    <div class="flex items-start justify-between gap-2 mb-2">
      <h4 class="font-medium text-gray-800 text-sm line-clamp-2">{{ task.title }}</h4>
      <span v-if="task.priority" class="priority-badge flex-shrink-0" :class="priorityClass">
        {{ priorityLabel }}
      </span>
    </div>

    <div v-if="task.tags && task.tags.length" class="flex flex-wrap gap-1 mb-2">
      <span
        v-for="tag in task.tags.slice(0, 3)"
        :key="tag"
        class="tag px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
      >
        {{ tag }}
      </span>
      <span v-if="task.tags.length > 3" class="text-xs text-gray-400">
        +{{ task.tags.length - 3 }}
      </span>
    </div>

    <div class="flex items-center justify-between text-xs text-gray-500">
      <div class="flex items-center gap-2">
        <span v-if="task.due_date" class="flex items-center gap-1" :class="{ 'text-red-500': isOverdue }">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {{ formatDate(task.due_date) }}
        </span>
      </div>
      <div class="flex items-center gap-1">
        <span v-if="task.comment_count" class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          {{ task.comment_count }}
        </span>
        <span v-if="task.subtask_count" class="flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          {{ task.subtask_count }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task, TaskPriority } from '@/api/tasks'

const props = defineProps<{
  task: Task
}>()

const priorityLabels: Record<TaskPriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent'
}

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-blue-100 text-blue-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700'
}

const priorityClass = computed(() => priorityColors[props.task.priority] || '')
const priorityLabel = computed(() => priorityLabels[props.task.priority] || '')

const isOverdue = computed(() => {
  if (!props.task.due_date) return false
  return new Date(props.task.due_date) < new Date()
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))

  if (days < 0) return `${Math.abs(days)}d overdue`
  if (days === 0) return 'Today'
  if (days === 1) return 'Tomorrow'
  if (days < 7) return `${days}d`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
