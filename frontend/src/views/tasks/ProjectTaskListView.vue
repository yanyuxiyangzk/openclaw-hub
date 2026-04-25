<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Tasks</h1>
        <p class="text-gray-500">{{ project?.name }}</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        + New Task
      </button>
    </div>

    <TaskFilter
      :filters="filters"
      :members="projectMembers"
      @update:filters="onFilterChange"
    />

    <div class="mt-4 bg-white border rounded-lg overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Task</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Priority</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Assignee</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Due Date</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="onTaskClick(task)"
          >
            <td class="px-4 py-3">
              <div class="font-medium text-gray-800">{{ task.title }}</div>
              <div v-if="task.tags?.length" class="flex gap-1 mt-1">
                <span
                  v-for="tag in task.tags.slice(0, 3)"
                  :key="tag"
                  class="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                >
                  {{ tag }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 text-xs rounded" :class="statusClass(task.status)">
                {{ statusLabel(task.status) }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 text-xs rounded" :class="priorityClass(task.priority)">
                {{ priorityLabel(task.priority) }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">
              {{ getAssigneeName(task.assignee_id) }}
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">
              {{ task.due_date ? formatDate(task.due_date) : '-' }}
            </td>
          </tr>
          <tr v-if="!tasks.length">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">
              No tasks found
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <TaskDetailDrawer
      :is-open="!!selectedTaskId"
      :task-id="selectedTaskId"
      :project-members="projectMembers"
      @close="selectedTaskId = null"
      @updated="loadTasks"
      @deleted="selectedTaskId = null; loadTasks()"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Project, ProjectMember } from '@/types'
import type { Task, TaskStatus, TaskPriority, TaskFilters } from '@/api/tasks'
import { getProject, getProjectMembers } from '@/api/projects'
import { listTasks } from '@/api/tasks'
import TaskFilter from '@/components/tasks/TaskFilter.vue'
import TaskDetailDrawer from '@/components/tasks/TaskDetailDrawer.vue'

const route = useRoute()
const projectId = route.params.id as string

const project = ref<Project | null>(null)
const projectMembers = ref<ProjectMember[]>([])
const tasks = ref<Task[]>([])
const selectedTaskId = ref<string | null>(null)
const showCreateModal = ref(false)

const filters = reactive<TaskFilters>({})

const statusLabels: Record<TaskStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  in_review: 'In Review',
  done: 'Done',
  blocked: 'Blocked'
}

const statusColors: Record<TaskStatus, string> = {
  todo: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-blue-100 text-blue-600',
  in_review: 'bg-yellow-100 text-yellow-600',
  done: 'bg-green-100 text-green-600',
  blocked: 'bg-red-100 text-red-600'
}

const priorityLabels: Record<TaskPriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent'
}

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-blue-100 text-blue-600',
  medium: 'bg-yellow-100 text-yellow-600',
  high: 'bg-orange-100 text-orange-600',
  urgent: 'bg-red-100 text-red-600'
}

const statusLabel = (s: TaskStatus) => statusLabels[s] || s
const statusClass = (s: TaskStatus) => statusColors[s] || ''
const priorityLabel = (p: TaskPriority) => priorityLabels[p] || p
const priorityClass = (p: TaskPriority) => priorityColors[p] || ''

const getAssigneeName = (assigneeId: string | null) => {
  if (!assigneeId) return '-'
  const member = projectMembers.value.find(m => m.user_id === assigneeId)
  return member?.user_name || member?.user_email || '-'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  })
}

const loadProject = async () => {
  const res = await getProject(projectId)
  if (res.data.code === 0) {
    project.value = res.data.data
  }
}

const loadMembers = async () => {
  const res = await getProjectMembers(projectId)
  if (res.data.code === 0) {
    projectMembers.value = res.data.data.items
  }
}

const loadTasks = async () => {
  const res = await listTasks({ project_id: projectId, ...filters })
  if (res.data.code === 0) {
    tasks.value = res.data.data.items
  }
}

const onFilterChange = (newFilters: TaskFilters) => {
  Object.assign(filters, newFilters)
  loadTasks()
}

const onTaskClick = (task: Task) => {
  selectedTaskId.value = task.id
}

onMounted(() => {
  loadProject()
  loadMembers()
  loadTasks()
})
</script>
