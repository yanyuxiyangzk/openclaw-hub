<template>
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-white font-medium">调度配置</h4>
    </div>

    <div class="space-y-4">
      <div>
        <label class="block text-gray-400 text-sm mb-1">任务名称</label>
        <input
          v-model="config.name"
          type="text"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="输入任务名称"
        />
      </div>

      <div>
        <label class="block text-gray-400 text-sm mb-1">Cron 表达式</label>
        <input
          v-model="config.cron_expression"
          type="text"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="* * * * *"
        />
        <p class="text-gray-500 text-xs mt-1">格式: 分 时 日 月 周</p>
      </div>

      <div>
        <label class="block text-gray-400 text-sm mb-1">Agent</label>
        <select
          v-model="config.agent_id"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">选择 Agent</option>
          <option v-for="agent in agents" :key="agent.id" :value="agent.id">
            {{ agent.name }}
          </option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <input
          v-model="config.enabled"
          type="checkbox"
          id="enabled"
          class="w-4 h-4 rounded bg-gray-700 border-gray-600 text-purple-500 focus:ring-purple-500"
        />
        <label for="enabled" class="text-gray-400 text-sm">启用调度</label>
      </div>

      <div class="flex gap-2 pt-2">
        <button
          v-if="showSave"
          @click="$emit('save', config)"
          :disabled="saving"
          class="px-4 py-2 bg-purple-500 text-white rounded text-sm hover:bg-purple-600 disabled:opacity-50"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button
          v-if="showTest"
          @click="$emit('test', config)"
          :disabled="testing"
          class="px-4 py-2 bg-gray-700 text-gray-300 rounded text-sm hover:bg-gray-600 disabled:opacity-50"
        >
          {{ testing ? '测试中...' : '测试执行' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="mt-3 text-red-400 text-sm">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import type { Agent } from '@/types'

interface SchedulerConfigData {
  name: string
  cron_expression: string
  agent_id: string
  enabled: boolean
}

const props = defineProps<{
  config?: SchedulerConfigData
  agents?: Agent[]
  showSave?: boolean
  showTest?: boolean
  saving?: boolean
  testing?: boolean
  error?: string
}>()

defineEmits<{
  save: [config: SchedulerConfigData]
  test: [config: SchedulerConfigData]
}>()

const config = reactive<SchedulerConfigData>({
  name: props.config?.name || '',
  cron_expression: props.config?.cron_expression || '',
  agent_id: props.config?.agent_id || '',
  enabled: props.config?.enabled ?? true,
})
</script>
