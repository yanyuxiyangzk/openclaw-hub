<template>
  <span
    :class="{
      'bg-yellow-500/20 text-yellow-400': status === 'pending',
      'bg-blue-500/20 text-blue-400': status === 'running',
      'bg-green-500/20 text-green-400': status === 'completed',
      'bg-red-500/20 text-red-400': status === 'failed',
      'bg-gray-500/20 text-gray-400': status === 'cancelled',
    }"
    class="px-2 py-1 rounded text-xs font-medium"
  >
    {{ statusText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const statusText = computed(() => {
  const texts: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return texts[props.status] || props.status
})
</script>
