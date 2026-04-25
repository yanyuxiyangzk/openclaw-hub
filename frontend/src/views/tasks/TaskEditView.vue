<template>
  <div class="p-6 max-w-4xl mx-auto">
    <div v-if="loading" class="text-center py-12 text-gray-400">
      Loading task...
    </div>

    <div v-else-if="!task" class="text-center py-12 text-gray-400">
      Task not found
    </div>

    <div v-else class="space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link
            :to="`/tasks/${taskId}`"
            class="p-2 hover:bg-gray-100 rounded-lg"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </router-link>
          <h1 class="text-2xl font-bold">Edit Task</h1>
        </div>
        <div class="flex gap-2">
          <button
            @click="goBack"
            class="px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="saveTask"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {{ error }}
      </div>

      <div class="bg-white border rounded-lg p-6 space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
          <input
            v-model="editForm.title"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            placeholder="Task title"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            v-model="editForm.description"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            rows="4"
            placeholder="Add description..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="editForm.status"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="in_review">In Review</option>
              <option value="done">Done</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Priority</label>
            <select
              v-model="editForm.priority"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
            <DueDatePicker v-model="editForm.due_date" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Reminder</label>
            <input
              type="datetime-local"
              v-model="editForm.reminder_at"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Estimated Hours</label>
            <input
              type="number"
              v-model.number="editForm.estimated_hours"
              min="0"
              step="0.5"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="0"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Actual Hours</label>
            <input
              type="number"
              v-model.number="editForm.actual_hours"
              min="0"
              step="0.5"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              placeholder="0"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Assignee</label>
          <select
            v-model="editForm.assignee_id"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Unassigned</option>
            <option v-for="member in projectMembers" :key="member.user_id" :value="member.user_id">
              {{ member.user_name || member.user_email }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tags</label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in editForm.tags"
              :key="tag"
              class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm flex items-center gap-1"
            >
              {{ tag }}
              <button @click="removeTag(tag)" class="hover:text-red-500">×</button>
            </span>
            <input
              v-model="newTag"
              @keydown.enter.prevent="addTag"
              placeholder="Add tag..."
              class="px-2 py-1 border rounded text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Task, TaskStatus, TaskPriority, TaskUpdate } from '@/api/tasks'
import type { ProjectMember } from '@/types'
import { getTask, updateTask as updateTaskApi } from '@/api/tasks'
import { getProjectMembers } from '@/api/projects'
import DueDatePicker from '@/components/tasks/DueDatePicker.vue'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id as string

const task = ref<Task | null>(null)
const projectMembers = ref<ProjectMember[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const newTag = ref('')

const editForm = reactive({
  title: '',
  description: '',
  status: 'todo' as TaskStatus,
  priority: 'medium' as TaskPriority,
  due_date: '',
  reminder_at: '',
  assignee_id: '',
  estimated_hours: null as number | null,
  actual_hours: null as number | null,
  tags: [] as string[]
})

const loadTask = async () => {
  try {
    const res = await getTask(taskId)
    if (res.data.code === 0) {
      task.value = res.data.data
      Object.assign(editForm, {
        title: task.value.title,
        description: task.value.description || '',
        status: task.value.status,
        priority: task.value.priority,
        due_date: task.value.due_date || '',
        reminder_at: task.value.reminder_at || '',
        assignee_id: task.value.assignee_id || '',
        estimated_hours: task.value.estimated_hours,
        actual_hours: task.value.actual_hours,
        tags: [...(task.value.tags || [])]
      })
    } else {
      error.value = res.data.message || 'Failed to load task'
    }
  } catch (e) {
    error.value = 'Failed to load task'
  }
}

const loadMembers = async () => {
  if (!task.value) return
  try {
    const res = await getProjectMembers(task.value.project_id)
    if (res.data.code === 0) {
      projectMembers.value = res.data.data.items
    }
  } catch (e) {
    // Silently fail - members are optional
  }
}

const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !editForm.tags.includes(tag)) {
    editForm.tags.push(tag)
  }
  newTag.value = ''
}

const removeTag = (tag: string) => {
  editForm.tags = editForm.tags.filter(t => t !== tag)
}

const saveTask = async () => {
  if (!editForm.title.trim()) {
    error.value = 'Title is required'
    return
  }

  saving.value = true
  error.value = ''

  try {
    const updateData: TaskUpdate = {
      title: editForm.title,
      description: editForm.description || undefined,
      status: editForm.status,
      priority: editForm.priority,
      due_date: editForm.due_date || undefined,
      reminder_at: editForm.reminder_at || undefined,
      assignee_id: editForm.assignee_id || undefined,
      estimated_hours: editForm.estimated_hours ?? undefined,
      actual_hours: editForm.actual_hours ?? undefined,
      tags: editForm.tags.length ? editForm.tags : undefined
    }

    const res = await updateTaskApi(taskId, updateData)
    if (res.data.code === 0) {
      router.push(`/tasks/${taskId}`)
    } else {
      error.value = res.data.message || 'Failed to update task'
    }
  } catch (e) {
    error.value = 'Failed to update task'
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push(`/tasks/${taskId}`)
}

onMounted(async () => {
  loading.value = true
  await loadTask()
  if (task.value) {
    await loadMembers()
  }
  loading.value = false
})
</script>
