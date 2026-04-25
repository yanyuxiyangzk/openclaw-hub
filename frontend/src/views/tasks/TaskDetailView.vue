<template>
  <div class="p-6 max-w-4xl mx-auto">
    <div v-if="loading" class="text-center py-12 text-gray-400">
      Loading task...
    </div>

    <div v-else-if="!task" class="text-center py-12 text-gray-400">
      Task not found
    </div>

    <div v-else class="space-y-6">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-2xl font-bold">{{ task.title }}</h1>
          <p class="text-gray-500 mt-1">in {{ project?.name }}</p>
        </div>
        <div class="flex gap-2">
          <router-link
            :to="`/projects/${task.project_id}/kanban`"
            class="px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            Back to Kanban
          </router-link>
          <router-link
            :to="`/tasks/${task.id}/edit`"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Edit
          </router-link>
        </div>
      </div>

      <div class="bg-white border rounded-lg p-6 space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-500 mb-2">Description</label>
          <p class="text-gray-800 whitespace-pre-wrap">
            {{ task.description || 'No description provided.' }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Status</label>
            <span class="px-3 py-1 rounded-lg text-sm" :class="statusClass(task.status)">
              {{ statusLabel(task.status) }}
            </span>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Priority</label>
            <span class="px-3 py-1 rounded-lg text-sm" :class="priorityClass(task.priority)">
              {{ priorityLabel(task.priority) }}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Due Date</label>
            <p class="text-gray-800">
              {{ task.due_date ? formatDate(task.due_date) : 'No due date' }}
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Assignee</label>
            <p class="text-gray-800">
              {{ assigneeName || 'Unassigned' }}
            </p>
          </div>
        </div>

        <div v-if="task.tags?.length">
          <label class="block text-sm font-medium text-gray-500 mb-2">Tags</label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in task.tags"
              :key="tag"
              class="px-2 py-1 bg-gray-100 text-gray-700 rounded"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Estimated Hours</label>
            <p class="text-gray-800">{{ task.estimated_hours ?? '-' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Actual Hours</label>
            <p class="text-gray-800">{{ task.actual_hours ?? '-' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-2">Progress</label>
            <p class="text-gray-800">{{ progress }}%</p>
          </div>
        </div>

        <div v-if="subtasks.length">
          <label class="block text-sm font-medium text-gray-500 mb-2">Subtasks</label>
          <div class="space-y-2">
            <div
              v-for="subtask in subtasks"
              :key="subtask.id"
              class="flex items-center gap-2 p-2 bg-gray-50 rounded"
            >
              <input
                type="checkbox"
                :checked="subtask.status === 'done'"
                @change="toggleSubtask(subtask)"
                class="w-4 h-4"
              />
              <span :class="{ 'line-through text-gray-400': subtask.status === 'done' }">
                {{ subtask.title }}
              </span>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-500 mb-2">Comments</label>
          <CommentThread
            :task-id="task.id"
            :comments="comments"
            @refresh="loadComments"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Task, TaskStatus, TaskPriority, TaskComment } from '@/api/tasks'
import type { Project, ProjectMember } from '@/types'
import { getTask, getComments, getSubtasks, updateTask } from '@/api/tasks'
import { getProject, getProjectMembers } from '@/api/projects'
import CommentThread from '@/components/tasks/CommentThread.vue'

const route = useRoute()
const taskId = route.params.id as string

const task = ref<Task | null>(null)
const project = ref<Project | null>(null)
const projectMembers = ref<ProjectMember[]>([])
const comments = ref<TaskComment[]>([])
const subtasks = ref<Task[]>([])
const loading = ref(true)

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

const assigneeName = computed(() => {
  if (!task.value?.assignee_id) return null
  const member = projectMembers.value.find(m => m.user_id === task.value!.assignee_id)
  return member?.user_name || member?.user_email
})

const progress = computed(() => {
  if (!subtasks.value.length) return 0
  const done = subtasks.value.filter(t => t.status === 'done').length
  return Math.round((done / subtasks.value.length) * 100)
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadTask = async () => {
  const res = await getTask(taskId)
  if (res.data.code === 0) {
    task.value = res.data.data
    const projRes = await getProject(task.value.project_id)
    if (projRes.data.code === 0) {
      project.value = projRes.data.data
    }
  }
}

const loadMembers = async () => {
  if (!task.value) return
  const res = await getProjectMembers(task.value.project_id)
  if (res.data.code === 0) {
    projectMembers.value = res.data.data.items
  }
}

const loadComments = async () => {
  const res = await getComments(taskId)
  if (res.data.code === 0) {
    comments.value = res.data.data.items
  }
}

const loadSubtasks = async () => {
  const res = await getSubtasks(taskId)
  if (res.data.code === 0) {
    subtasks.value = res.data.data.items
  }
}

const toggleSubtask = async (subtask: Task) => {
  const newStatus = subtask.status === 'done' ? 'todo' : 'done'
  await updateTask(subtask.id, { status: newStatus })
  await loadSubtasks()
}

onMounted(async () => {
  loading.value = true
  await loadTask()
  if (task.value) {
    await Promise.all([loadMembers(), loadComments(), loadSubtasks()])
  }
  loading.value = false
})
</script>
