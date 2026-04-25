<template>
  <div class="space-y-2">
    <div v-if="subtasks.length" class="space-y-2">
      <div
        v-for="subtask in subtasks"
        :key="subtask.id"
        class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg"
      >
        <input
          type="checkbox"
          :checked="subtask.status === 'done'"
          @change="toggleSubtask(subtask)"
          class="w-4 h-4 text-blue-600 rounded"
        />
        <span
          class="flex-1 text-sm"
          :class="{ 'line-through text-gray-400': subtask.status === 'done' }"
        >
          {{ subtask.title }}
        </span>
        <span
          class="px-2 py-0.5 text-xs rounded"
          :class="statusClass(subtask.status)"
        >
          {{ statusLabel(subtask.status) }}
        </span>
      </div>
    </div>
    <div v-else class="text-sm text-gray-400">No subtasks</div>
  </div>
</template>

<script setup lang="ts">
import type { Task, TaskStatus } from '@/api/tasks'
import { updateTask } from '@/api/tasks'

defineProps<{
  taskId: string
  subtasks: Task[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const statusLabels: Record<TaskStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  in_review: 'Review',
  done: 'Done',
  blocked: 'Blocked'
}

const statusClass = (status: TaskStatus) => {
  const classes: Record<TaskStatus, string> = {
    todo: 'bg-gray-100 text-gray-600',
    in_progress: 'bg-blue-100 text-blue-600',
    in_review: 'bg-yellow-100 text-yellow-600',
    done: 'bg-green-100 text-green-600',
    blocked: 'bg-red-100 text-red-600'
  }
  return classes[status]
}

const statusLabel = (status: TaskStatus) => statusLabels[status]

const toggleSubtask = async (subtask: Task) => {
  const newStatus = subtask.status === 'done' ? 'todo' : 'done'
  await updateTask(subtask.id, { status: newStatus })
  emit('refresh')
}
</script>
