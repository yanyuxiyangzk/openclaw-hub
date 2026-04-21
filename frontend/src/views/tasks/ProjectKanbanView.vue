<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Kanban Board</h1>
        <p class="text-gray-500">{{ project?.name }}</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        + New Task
      </button>
    </div>

    <KanbanBoard
      ref="kanbanRef"
      :project-id="projectId"
      @task-click="onTaskClick"
    />

    <TaskDetailDrawer
      :is-open="!!selectedTaskId"
      :task-id="selectedTaskId"
      :project-members="projectMembers"
      @close="selectedTaskId = null"
      @updated="kanbanRef?.reload()"
      @deleted="selectedTaskId = null"
    />

    <!-- Create Task Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center"
    >
      <div class="absolute inset-0 bg-black/30" @click="showCreateModal = false"></div>
      <div class="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Create Task</h2>
        <form @submit.prevent="createTask" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              v-model="newTask.title"
              required
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="newTask.description"
              rows="3"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                v-model="newTask.priority"
                class="w-full border rounded-lg px-3 py-2"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input
                type="date"
                v-model="newTask.due_date"
                class="w-full border rounded-lg px-3 py-2"
              />
            </div>
          </div>
          <div class="flex gap-2 justify-end pt-4">
            <button
              type="button"
              @click="showCreateModal = false"
              class="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Project, ProjectMember } from '@/types'
import { getProject, getProjectMembers } from '@/api/projects'
import { createTask as createTaskApi } from '@/api/tasks'
import KanbanBoard from '@/components/tasks/KanbanBoard.vue'
import TaskDetailDrawer from '@/components/tasks/TaskDetailDrawer.vue'

const route = useRoute()
const projectId = route.params.id as string

const project = ref<Project | null>(null)
const projectMembers = ref<ProjectMember[]>([])
const selectedTaskId = ref<string | null>(null)
const showCreateModal = ref(false)
const kanbanRef = ref<InstanceType<typeof KanbanBoard> | null>(null)

const newTask = ref({
  title: '',
  description: '',
  priority: 'medium',
  due_date: ''
})

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

const onTaskClick = (task: any) => {
  selectedTaskId.value = task.id
}

const createTask = async () => {
  const res = await createTaskApi({
    title: newTask.value.title,
    description: newTask.value.description,
    project_id: projectId,
    priority: newTask.value.priority as any,
    due_date: newTask.value.due_date || undefined
  })
  if (res.data.code === 0) {
    showCreateModal.value = false
    newTask.value = { title: '', description: '', priority: 'medium', due_date: '' }
    kanbanRef.value?.reload()
  }
}

onMounted(() => {
  loadProject()
  loadMembers()
})
</script>
