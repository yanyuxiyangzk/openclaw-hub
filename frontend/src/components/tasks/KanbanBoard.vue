<template>
  <div class="kanban-board flex gap-4 overflow-x-auto pb-4">
    <KanbanColumn
      v-for="column in columns"
      :key="column.status"
      :column="column"
      :project-id="projectId"
      @task-click="onTaskClick"
      @task-moved="onTaskMoved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { KanbanBoard as KanbanBoardType, KanbanColumn as KanbanColumnType, Task, TaskStatus } from '@/api/tasks'
import { getKanbanBoard, moveTask } from '@/api/tasks'
import KanbanColumn from './KanbanColumn.vue'

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  taskClick: [task: Task]
}>()

const columns = ref<KanbanColumnType[]>([])

const loadBoard = async () => {
  const res = await getKanbanBoard(props.projectId)
  if (res.data.code === 0) {
    columns.value = res.data.data.columns
  }
}

const onTaskClick = (task: Task) => {
  emit('taskClick', task)
}

const onTaskMoved = async (taskId: string, newStatus: TaskStatus, newPosition: number) => {
  await moveTask(taskId, { status: newStatus, position: newPosition })
  await loadBoard()
}

onMounted(() => {
  loadBoard()
})

defineExpose({ reload: loadBoard })
</script>
