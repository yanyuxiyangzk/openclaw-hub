<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex justify-end"
    @click.self="close"
  >
    <div class="absolute inset-0 bg-black/30" @click="close"></div>
    <div class="relative w-full max-w-2xl bg-white shadow-xl overflow-y-auto">
      <div class="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold">Task Details</h2>
        <button
          @click="close"
          class="p-1 hover:bg-gray-100 rounded"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div v-if="task" class="p-6 space-y-6">
        <!-- Title & Description -->
        <div>
          <input
            v-model="editForm.title"
            class="text-xl font-semibold w-full border-0 border-b border-transparent focus:border-blue-500 focus:ring-0 px-0 py-1"
            placeholder="Task title"
            @blur="updateTask"
          />
          <textarea
            v-model="editForm.description"
            class="mt-2 w-full border rounded-lg p-3 text-gray-600 focus:ring-2 focus:ring-blue-500"
            rows="3"
            placeholder="Add description..."
            @blur="updateTask"
          ></textarea>
        </div>

        <!-- Status & Priority -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="editForm.status"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              @change="updateTask"
            >
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="in_review">In Review</option>
              <option value="done">Done</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              v-model="editForm.priority"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              @change="updateTask"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        <!-- Due Date & Reminder -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
            <DueDatePicker v-model="editForm.due_date" @change="updateTask" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Reminder</label>
            <input
              type="datetime-local"
              v-model="editForm.reminder_at"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              @change="updateTask"
            />
          </div>
        </div>

        <!-- Assignee -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
          <select
            v-model="editForm.assignee_id"
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            @change="updateTask"
          >
            <option value="">Unassigned</option>
            <option v-for="member in projectMembers" :key="member.user_id" :value="member.user_id">
              {{ member.user_name || member.user_email }}
            </option>
          </select>
        </div>

        <!-- Tags -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tags</label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in task.tags"
              :key="tag"
              class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm flex items-center gap-1"
            >
              {{ tag }}
              <button @click="removeTag(tag)" class="hover:text-red-500">×</button>
            </span>
            <input
              v-model="newTag"
              @keydown.enter="addTag"
              placeholder="Add tag..."
              class="px-2 py-1 border rounded text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- Subtasks -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700">Subtasks</label>
            <button
              @click="showSubtaskForm = true"
              class="text-sm text-blue-600 hover:text-blue-700"
            >
              + Add subtask
            </button>
          </div>
          <SubtaskList
            :task-id="task.id"
            :subtasks="subtasks"
            @refresh="loadSubtasks"
          />
        </div>

        <!-- Comments -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Comments</label>
          <CommentThread
            :task-id="task.id"
            :comments="comments"
            @refresh="loadComments"
          />
        </div>

        <!-- Activity -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Activity</label>
          <div class="space-y-2 text-sm text-gray-600">
            <div v-for="activity in activities" :key="activity.id" class="flex items-start gap-2">
              <span class="font-medium">{{ activity.user_name || activity.user_email }}</span>
              <span>{{ activity.action }}</span>
              <span class="text-gray-400">{{ formatDate(activity.created_at) }}</span>
            </div>
            <div v-if="!activities.length" class="text-gray-400">No activity yet</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 pt-4 border-t">
          <button
            @click="completeTask"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Complete
          </button>
          <button
            @click="deleteTask"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import type { Task, TaskComment, TaskActivity, ProjectMember } from '@/api/tasks'
import {
  getTask, updateTask as updateTaskApi, deleteTask as deleteTaskApi,
  getComments, addComment, getSubtasks, getActivity, completeTask as completeTaskApi
} from '@/api/tasks'
import CommentThread from './CommentThread.vue'
import SubtaskList from './SubtaskList.vue'
import DueDatePicker from './DueDatePicker.vue'

const props = defineProps<{
  isOpen: boolean
  taskId: string | null
  projectMembers?: ProjectMember[]
}>()

const emit = defineEmits<{
  close: []
  updated: []
  deleted: []
}>()

const task = ref<Task | null>(null)
const comments = ref<TaskComment[]>([])
const subtasks = ref<Task[]>([])
const activities = ref<TaskActivity[]>([])
const newTag = ref('')
const showSubtaskForm = ref(false)

const editForm = reactive({
  title: '',
  description: '',
  status: 'todo' as string,
  priority: 'medium' as string,
  due_date: '',
  reminder_at: '',
  assignee_id: ''
})

const close = () => {
  emit('close')
}

const loadTask = async () => {
  if (!props.taskId) return
  const res = await getTask(props.taskId)
  if (res.data.code === 0) {
    task.value = res.data.data
    Object.assign(editForm, {
      title: task.value.title,
      description: task.value.description || '',
      status: task.value.status,
      priority: task.value.priority,
      due_date: task.value.due_date || '',
      reminder_at: task.value.reminder_at || '',
      assignee_id: task.value.assignee_id || ''
    })
  }
}

const loadComments = async () => {
  if (!props.taskId) return
  const res = await getComments(props.taskId)
  if (res.data.code === 0) {
    comments.value = res.data.data.items
  }
}

const loadSubtasks = async () => {
  if (!props.taskId) return
  const res = await getSubtasks(props.taskId)
  if (res.data.code === 0) {
    subtasks.value = res.data.data.items
  }
}

const loadActivity = async () => {
  if (!props.taskId) return
  const res = await getActivity(props.taskId)
  if (res.data.code === 0) {
    activities.value = res.data.data
  }
}

const updateTask = async () => {
  if (!props.taskId) return
  await updateTaskApi(props.taskId, {
    title: editForm.title,
    description: editForm.description,
    status: editForm.status,
    priority: editForm.priority,
    due_date: editForm.due_date || undefined,
    reminder_at: editForm.reminder_at || undefined,
    assignee_id: editForm.assignee_id || undefined
  })
  emit('updated')
}

const addTag = async () => {
  if (!newTag.value.trim() || !task.value) return
  const tags = [...(task.value.tags || []), newTag.value.trim()]
  await updateTaskApi(props.taskId!, { tags: [...new Set(tags)] })
  newTag.value = ''
  await loadTask()
  emit('updated')
}

const removeTag = async (tag: string) => {
  if (!task.value) return
  const tags = (task.value.tags || []).filter(t => t !== tag)
  await updateTaskApi(props.taskId!, { tags })
  await loadTask()
  emit('updated')
}

const completeTask = async () => {
  if (!props.taskId) return
  await completeTaskApi(props.taskId)
  await loadTask()
  emit('updated')
}

const deleteTask = async () => {
  if (!props.taskId) return
  if (confirm('Are you sure you want to delete this task?')) {
    await deleteTaskApi(props.taskId)
    emit('deleted')
    close()
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

watch(() => props.taskId, () => {
  if (props.taskId) {
    loadTask()
    loadComments()
    loadSubtasks()
    loadActivity()
  }
}, { immediate: true })

watch(() => props.isOpen, (val) => {
  if (val && props.taskId) {
    loadTask()
    loadComments()
    loadSubtasks()
    loadActivity()
  }
})
</script>
