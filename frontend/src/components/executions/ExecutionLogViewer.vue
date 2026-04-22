<template>
  <div class="bg-gray-900 rounded-lg p-4 font-mono text-sm">
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-gray-400 text-xs uppercase">执行日志</h4>
      <button
        v-if="refreshable"
        @click="$emit('refresh')"
        class="text-xs text-purple-400 hover:text-purple-300"
      >
        刷新
      </button>
    </div>
    <div v-if="loading" class="text-gray-500">加载中...</div>
    <div v-else-if="!logs || logs.length === 0" class="text-gray-600">暂无日志</div>
    <div v-else class="space-y-1 max-h-64 overflow-y-auto">
      <div
        v-for="(log, idx) in logs"
        :key="idx"
        :class="{
          'text-red-400': log.level === 'error',
          'text-yellow-400': log.level === 'warning',
          'text-green-400': log.level === 'info',
          'text-gray-500': log.level === 'debug',
        }"
      >
        <span class="text-gray-600">[{{ formatTime(log.timestamp) }}]</span>
        <span class="ml-2">{{ log.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface LogEntry {
  timestamp: string
  level: string
  message: string
}

defineProps<{
  logs?: LogEntry[]
  loading?: boolean
  refreshable?: boolean
}>()

defineEmits<{
  refresh: []
}>()

const formatTime = (timestamp: string) => {
  try {
    const date = new Date(timestamp)
    return date.toLocaleTimeString()
  } catch {
    return timestamp
  }
}
</script>
