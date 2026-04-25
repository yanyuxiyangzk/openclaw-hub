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

const onDrop = async (event: DragEvent) => {
  if (!draggedTask.value) return

  // Find the task list element
  const taskListEl = (event.target as HTMLElement).closest('.task-list') as HTMLElement
  if (!taskListEl) return

  // Get all task cards except the dragged one
  const taskCards = Array.from(taskListEl.querySelectorAll('.task-card')) as HTMLElement[]
  const validCards = taskCards.filter(card => !card.classList.contains('opacity-50'))

  let dropIndex = validCards.length
  const mouseY = event.clientY

  for (let i = 0; i < validCards.length; i++) {
    const rect = validCards[i].getBoundingClientRect()
    if (mouseY < rect.top + rect.height / 2) {
      dropIndex = i
      break
    }
  }

  // Emit task-moved if status changed OR position changed
  const hasStatusChanged = draggedTask.value.status !== props.column.status
  const currentIndex = props.column.tasks.findIndex(t => t.id === draggedTask.value!.id)
  const hasPositionChanged = currentIndex !== -1 && dropIndex !== currentIndex

  if (hasStatusChanged || hasPositionChanged) {
    emit('taskMoved', draggedTask.value.id, props.column.status, dropIndex)
  }

  draggedTask.value = null
}
</script>
