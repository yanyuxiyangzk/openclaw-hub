<template>
  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-white font-medium">工作流编辑器</h4>
      <button
        @click="addStep"
        class="text-sm text-purple-400 hover:text-purple-300"
      >
        + 添加步骤
      </button>
    </div>

    <div class="space-y-3">
      <div
        v-for="(step, idx) in steps"
        :key="idx"
        class="bg-gray-700 rounded-lg p-3 border border-gray-600"
      >
        <div class="flex items-start gap-3">
          <div class="flex-1 space-y-2">
            <div class="flex gap-2">
              <input
                v-model="step.step_id"
                type="text"
                placeholder="步骤ID"
                class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
              <input
                v-model="step.name"
                type="text"
                placeholder="步骤名称"
                class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
            <div class="flex gap-2">
              <input
                v-model="step.task_template_id"
                type="text"
                placeholder="任务模板ID"
                class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
              <input
                v-model="step.agent_id"
                type="text"
                placeholder="Agent ID"
                class="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
            <input
              v-model="step.depends_on"
              type="text"
              placeholder="依赖步骤 (逗号分隔)"
              class="w-full px-2 py-1 bg-gray-600 border border-gray-500 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>
          <button
            @click="removeStep(idx)"
            class="text-red-400 hover:text-red-300 p-1"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div v-if="!steps.length" class="text-gray-500 text-center py-4 text-sm">
      点击"添加步骤"开始创建工作流
    </div>

    <div class="flex gap-2 mt-4">
      <button
        v-if="showSave"
        @click="$emit('save', steps)"
        :disabled="saving"
        class="px-4 py-2 bg-purple-500 text-white rounded text-sm hover:bg-purple-600 disabled:opacity-50"
      >
        {{ saving ? '保存中...' : '保存工作流' }}
      </button>
      <button
        v-if="showExecute"
        @click="$emit('execute')"
        :disabled="executing || !steps.length"
        class="px-4 py-2 bg-green-500 text-white rounded text-sm hover:bg-green-600 disabled:opacity-50"
      >
        {{ executing ? '执行中...' : '执行工作流' }}
      </button>
    </div>

    <div v-if="error" class="mt-3 text-red-400 text-sm">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import type { WorkflowStep } from '@/api/workflows'

const props = defineProps<{
  steps?: WorkflowStep[]
  showSave?: boolean
  showExecute?: boolean
  saving?: boolean
  executing?: boolean
  error?: string
}>()

defineEmits<{
  save: [steps: WorkflowStep[]]
  execute: []
}>()

const steps = reactive<WorkflowStep[]>(
  props.steps?.map(s => ({ ...s })) || []
)

const addStep = () => {
  steps.push({
    step_id: `step_${steps.length + 1}`,
    name: '',
    task_template_id: '',
    agent_id: '',
    depends_on: [],
  })
}

const removeStep = (idx: number) => {
  steps.splice(idx, 1)
}
</script>
