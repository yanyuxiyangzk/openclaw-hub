<template>
  <div class="bg-white border rounded-lg p-4 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="font-medium">Filters</h3>
      <button
        @click="reset"
        class="text-sm text-blue-600 hover:text-blue-700"
      >
        Reset
      </button>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div>
        <label class="block text-sm text-gray-600 mb-1">Status</label>
        <select
          :value="filters.status"
          @change="$emit('update:filters', { ...filters, status: ($event.target as HTMLSelectElement).value || undefined })"
          class="w-full border rounded px-2 py-1.5 text-sm"
        >
          <option value="">All</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="done">Done</option>
          <option value="blocked">Blocked</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Priority</label>
        <select
          :value="filters.priority"
          @change="$emit('update:filters', { ...filters, priority: ($event.target as HTMLSelectElement).value || undefined })"
          class="w-full border rounded px-2 py-1.5 text-sm"
        >
          <option value="">All</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Assignee</label>
        <select
          :value="filters.assignee_id"
          @change="$emit('update:filters', { ...filters, assignee_id: ($event.target as HTMLSelectElement).value || undefined })"
          class="w-full border rounded px-2 py-1.5 text-sm"
        >
          <option value="">All</option>
          <option v-for="member in members" :key="member.user_id" :value="member.user_id">
            {{ member.user_name || member.user_email }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Due Date</label>
        <select
          :value="filters.due"
          @change="$emit('update:filters', { ...filters, due: ($event.target as HTMLSelectElement).value || undefined })"
          class="w-full border rounded px-2 py-1.5 text-sm"
        >
          <option value="">All</option>
          <option value="overdue">Overdue</option>
          <option value="today">Today</option>
          <option value="this_week">This Week</option>
          <option value="no_date">No Date</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProjectMember } from '@/types'

interface TaskFilters {
  status?: string
  priority?: string
  assignee_id?: string
  due?: string
}

defineProps<{
  filters: TaskFilters
  members: ProjectMember[]
}>()

defineEmits<{
  'update:filters': [filters: TaskFilters]
}>()

const reset = () => {
  window.location.reload()
}
</script>
