<template>
  <div class="space-y-4">
    <TaskFilter
      v-if="showFilter"
      :filters="filters"
      :members="members"
      @update:filters="onFilterUpdate"
    />
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { KanbanColumn as KanbanColumnType, Task, TaskStatus, TaskFilters } from '@/api/tasks'
import { getKanbanBoard, moveTask } from '@/api/tasks'
import type { ProjectMember } from '@/types'
import KanbanColumn from './KanbanColumn.vue'
import TaskFilter from './TaskFilter.vue'

const props = defineProps<{
  projectId: string
  members?: ProjectMember[]
  showFilter?: boolean
}>()

const emit = defineEmits<{
  taskClick: [task: Task]
}>()

const columns = ref<KanbanColumnType[]>([])
const filters = ref<TaskFilters>({})

const buildFilterParams = () => {
  const params: {
    priority?: TaskStatus
    assignee_id?: string
    due?: 'overdue' | 'today' | 'this_week' | 'no_date'
    tags?: string
  } = {}

  if (filters.value.priority) params.priority = filters.value.priority
  if (filters.value.assignee_id) params.assignee_id = filters.value.assignee_id
  if (filters.value.due) params.due = filters.value.due
  if (filters.value.tags && filters.value.tags.length > 0) {
    params.tags = filters.value.tags.join(',')
  }

  return params
}

const loadBoard = async () => {
  const params = buildFilterParams()
  const res = await getKanbanBoard(props.projectId, Object.keys(params).length > 0 ? params : undefined)
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

const onFilterUpdate = (newFilters: TaskFilters) => {
  filters.value = newFilters
  loadBoard()
}

onMounted(() => {
  loadBoard()
})

defineExpose({ reload: loadBoard, setFilters: (f: TaskFilters) => { filters.value = f; loadBoard() } })
</script>
