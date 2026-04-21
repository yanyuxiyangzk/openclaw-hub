<template>
  <div class="space-y-3">
    <div v-if="comments.length" class="space-y-3">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="bg-gray-50 rounded-lg p-3"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="font-medium text-sm text-gray-800">
            {{ comment.author_name || comment.author_email || 'Unknown' }}
          </span>
          <span class="text-xs text-gray-400">{{ formatDate(comment.created_at) }}</span>
        </div>
        <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ comment.content }}</p>
      </div>
    </div>
    <div v-else class="text-sm text-gray-400">No comments yet</div>

    <div class="flex gap-2">
      <textarea
        v-model="newComment"
        placeholder="Add a comment..."
        class="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
        rows="2"
        @keydown.ctrl.enter="submitComment"
      ></textarea>
      <button
        @click="submitComment"
        :disabled="!newComment.trim()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { TaskComment } from '@/api/tasks'
import { addComment } from '@/api/tasks'

const props = defineProps<{
  taskId: string
  comments: TaskComment[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const newComment = ref('')

const submitComment = async () => {
  if (!newComment.value.trim()) return
  await addComment(props.taskId, newComment.value)
  newComment.value = ''
  emit('refresh')
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(mins / 60)
  const days = Math.floor(hours / 24)

  if (mins > -1) return 'Just now'
  if (mins > -60) return `${Math.abs(mins)}m ago`
  if (hours > -24) return `${Math.abs(hours)}h ago`
  if (days > -7) return `${Math.abs(days)}d ago`
  return date.toLocaleDateString()
}
</script>
