<template>
  <div class="kanban-column min-w-[280px] max-w-[320px] bg-gray-50 rounded-lg p-3">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold text-gray-700">{{ columnTitle }}</h3>
      <span class="badge bg-gray-200 text-gray-600 px-2 py-0.5 rounded text-sm">{{ column.count }}</span>
    </div>
    <div
      class="task-list min-h-[200px] space-y-2"
      @dragover.prevent
      @drop="onDrop"
    >
      <TaskCard
        v-for="task in column.tasks"
        :key="task.id"
        :task="task"
        draggable="true"
        @dragstart="onDragStart(task)"
        @click="$emit('taskClick', task)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { KanbanColumn as KanbanColumnType, Task, TaskStatus } from '@/api/tasks'
import TaskCard from './TaskCard.vue'

const props = defineProps<{
  column: KanbanColumnType
  projectId: string
}>()

const emit = defineEmits<{
  taskClick: [task: Task]
  taskMoved: [taskId: string, newStatus: TaskStatus, newPosition: number]
}>()

const statusLabels: Record<TaskStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  in_review: 'In Review',
  done: 'Done',
  blocked: 'Blocked'
}

const columnTitle = computed(() => statusLabels[props.column.status] || props.column.status)

const draggedTask = ref<Task | null>(null)

const onDragStart = (task: Task) => {
  draggedTask.value = task
}

const onDrop = async () => {
  if (draggedTask.value && draggedTask.value.status !== props.column.status) {
    emit('taskMoved', draggedTask.value.id, props.column.status, props.column.tasks.length)
    draggedTask.value = null
  }
}
</script>
