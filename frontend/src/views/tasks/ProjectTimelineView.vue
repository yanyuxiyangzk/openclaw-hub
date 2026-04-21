<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Timeline</h1>
      <p class="text-gray-500">{{ project?.name }}</p>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">
      Loading timeline...
    </div>

    <div v-else-if="!tasks.length" class="text-center py-12 text-gray-400">
      No tasks with due dates
    </div>

    <div v-else class="relative">
      <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

      <div class="space-y-6">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="relative pl-10"
          @click="onTaskClick(task)"
        >
          <div
            class="absolute left-2 w-4 h-4 rounded-full border-2 bg-white"
            :class="isOverdue(task) ? 'border-red-500 bg-red-100' : 'border-blue-500 bg-blue-100'"
          ></div>

          <div
            class="bg-white border rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-medium text-gray-800">{{ task.title }}</h3>
                <p v-if="task.description" class="text-sm text-gray-500 mt-1 line-clamp-2">
                  {{ task.description }}
                </p>
              </div>
              <span
                class="px-2 py-1 text-xs rounded"
                :class="statusClass(task.status)"
              >
                {{ statusLabel(task.status) }}
              </span>
            </div>

            <div class="flex items-center gap-4 mt-3 text-sm text-gray-500">
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(task.due_date!) }}
              </span>
              <span v-if="task.assignee_id" class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {{ getAssigneeName(task.assignee_id) }}
              </span>
            </div>

            <div v-if="getSubtaskProgress(task)" class="mt-3">
              <div class="flex items-center gap-2 text-sm">
                <span class="text-gray-500">Progress:</span>
                <div class="flex-1 max-w-[200px] h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-blue-500"
                    :style="{ width: `${getSubtaskProgress(task)}%` }"
                  ></div>
                </div>
                <span class="text-gray-500">{{ getSubtaskProgress(task) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <TaskDetailDrawer
      :is-open="!!selectedTaskId"
      :task-id="selectedTaskId"
      :project-members="projectMembers"
      @close="selectedTaskId = null"
      @updated="loadTimeline"
      @deleted="selectedTaskId = null; loadTimeline()"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Project, ProjectMember } from '@/types'
import type { Task, TaskStatus } from '@/api/tasks'
import { getProject, getProjectMembers } from '@/api/projects'
import { getTimeline, getSubtasks } from '@/api/tasks'
import TaskDetailDrawer from '@/components/tasks/TaskDetailDrawer.vue'

const route = useRoute()
const projectId = route.params.id as string

const project = ref<Project | null>(null)
const projectMembers = ref<ProjectMember[]>([])
const tasks = ref<Task[]>([])
const subtasksMap = ref<Record<string, Task[]>>({})
const loading = ref(true)
const selectedTaskId = ref<string | null>(null)

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

const statusLabel = (s: TaskStatus) => statusLabels[s] || s
const statusClass = (s: TaskStatus) => statusColors[s] || ''

const isOverdue = (task: Task) => {
  if (!task.due_date) return false
  return new Date(task.due_date) < new Date() && task.status !== 'done'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}

const getAssigneeName = (assigneeId: string) => {
  const member = projectMembers.value.find(m => m.user_id === assigneeId)
  return member?.user_name || member?.user_email || '-'
}

const getSubtaskProgress = (task: Task): number => {
  const subtasks = subtasksMap.value[task.id] || []
  if (!subtasks.length) return 0
  const done = subtasks.filter(t => t.status === 'done').length
  return Math.round((done / subtasks.length) * 100)
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

const loadTimeline = async () => {
  loading.value = true
  const res = await getTimeline(projectId)
  if (res.data.code === 0) {
    tasks.value = res.data.data
    for (const task of tasks.value) {
      const subRes = await getSubtasks(task.id)
      if (subRes.data.code === 0) {
        subtasksMap.value[task.id] = subRes.data.data.items
      }
    }
  }
  loading.value = false
}

const onTaskClick = (task: Task) => {
  selectedTaskId.value = task.id
}

onMounted(() => {
  loadProject()
  loadMembers()
  loadTimeline()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
