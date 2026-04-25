<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Due Soon</h1>
      <p class="text-gray-500">Tasks requiring attention</p>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">
      Loading...
    </div>

    <div v-else class="space-y-6">
      <div class="grid grid-cols-4 gap-4">
        <div class="bg-white border rounded-lg p-4">
          <div class="text-2xl font-bold text-red-600">{{ summary.overdue }}</div>
          <div class="text-sm text-gray-500">Overdue</div>
        </div>
        <div class="bg-white border rounded-lg p-4">
          <div class="text-2xl font-bold text-orange-600">{{ summary.due_today }}</div>
          <div class="text-sm text-gray-500">Due Today</div>
        </div>
        <div class="bg-white border rounded-lg p-4">
          <div class="text-2xl font-bold text-yellow-600">{{ summary.due_this_week }}</div>
          <div class="text-sm text-gray-500">Due This Week</div>
        </div>
        <div class="bg-white border rounded-lg p-4">
          <div class="text-2xl font-bold text-blue-600">{{ summary.total }}</div>
          <div class="text-sm text-gray-500">Total</div>
        </div>
      </div>

      <div class="space-y-3">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="bg-white border rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
          @click="onTaskClick(task)"
        >
          <div class="flex items-start justify-between">
            <div>
              <h3 class="font-medium text-gray-800">{{ task.title }}</h3>
              <p v-if="task.description" class="text-sm text-gray-500 mt-1 line-clamp-1">
                {{ task.description }}
              </p>
            </div>
            <span
              class="px-2 py-1 text-xs rounded"
              :class="isOverdue(task) ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'"
            >
              {{ getDueLabel(task) }}
            </span>
          </div>
          <div class="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <span>{{ getProjectName(task.project_id) }}</span>
            <span v-if="task.due_date">{{ formatDate(task.due_date) }}</span>
            <span v-if="task.assignee_id">{{ getAssigneeName(task.assignee_id) }}</span>
          </div>
        </div>

        <div v-if="!tasks.length" class="text-center py-12 text-gray-400">
          No tasks due soon
        </div>
      </div>
    </div>

    <TaskDetailDrawer
      :is-open="!!selectedTaskId"
      :task-id="selectedTaskId"
      @close="selectedTaskId = null"
      @updated="loadTasks"
      @deleted="selectedTaskId = null; loadTasks()"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { Task, DueSoonTasks as DueSoonTasksType } from '@/api/tasks'
import { getDueSoonTasks } from '@/api/tasks'
import TaskDetailDrawer from '@/components/tasks/TaskDetailDrawer.vue'

const tasks = ref<Task[]>([])
const loading = ref(true)
const selectedTaskId = ref<string | null>(null)

const summary = reactive({
  total: 0,
  overdue: 0,
  due_today: 0,
  due_this_week: 0
})

const getDueLabel = (task: Task): string => {
  if (!task.due_date) return 'No date'
  const now = new Date()
  const due = new Date(task.due_date)
  const diff = due.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))

  if (days < 0) return `${Math.abs(days)}d overdue`
  if (days === 0) return 'Due today'
  if (days === 1) return 'Due tomorrow'
  if (days <= 7) return `Due in ${days}d`
  return `Due ${due.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
}

const isOverdue = (task: Task) => {
  if (!task.due_date) return false
  return new Date(task.due_date) < new Date() && task.status !== 'done'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getProjectName = (_projectId: string) => {
  return 'Project'
}

const getAssigneeName = (_assigneeId: string) => {
  return 'Assignee'
}

const loadTasks = async () => {
  loading.value = true
  const res = await getDueSoonTasks(168)
  if (res.data.code === 0) {
    const data: DueSoonTasksType = res.data.data
    tasks.value = data.tasks
    summary.total = data.total
    summary.overdue = data.overdue
    summary.due_today = data.due_today
    summary.due_this_week = data.due_this_week
  }
  loading.value = false
}

const onTaskClick = (task: Task) => {
  selectedTaskId.value = task.id
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
