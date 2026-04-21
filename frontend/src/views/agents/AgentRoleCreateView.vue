<template>
  <AppLayout>
    <div class="max-w-2xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push('/agent-roles')" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">创建角色模板</h2>
        </div>
      </div>

      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <form @submit.prevent="handleCreate">
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">角色名称 *</label>
            <input
              v-model="form.name"
              type="text"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="例如: 代码助手、数据分析师"
              required
              maxlength="64"
            />
          </div>

          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">描述</label>
            <textarea
              v-model="form.description"
              rows="2"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="描述此角色的职责和能力"
            ></textarea>
          </div>

          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">系统提示词模板</label>
            <textarea
              v-model="form.system_prompt_template"
              rows="6"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              placeholder="定义 Agent 的行为模式、语气、专业知识等...

例如:
你是一个专业的代码助手，擅长:
- 编写高质量的 Python/JavaScript 代码
- 代码审查和优化建议
- 解释复杂的技术概念"
            ></textarea>
            <p class="mt-2 text-gray-500 text-xs">
              此模板将作为 Agent 的系统提示词，影响其回复风格和能力范围。
            </p>
          </div>

          <div class="mb-6">
            <label class="block text-gray-400 mb-2 text-sm">默认配置 (JSON)</label>
            <textarea
              v-model="configJson"
              rows="4"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              placeholder='{"temperature": 0.7, "max_tokens": 2000}'
            ></textarea>
            <p v-if="configError" class="mt-2 text-red-400 text-xs">{{ configError }}</p>
          </div>

          <p v-if="createError" class="mb-4 text-sm text-red-400">{{ createError }}</p>

          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="createLoading"
              class="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 transition"
            >
              {{ createLoading ? '创建中...' : '创建角色' }}
            </button>
            <button
              type="button"
              @click="router.push('/agent-roles')"
              class="px-6 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import * as phase3Api from '@/api/phase3'

const router = useRouter()

const form = ref({
  name: '',
  description: '',
  system_prompt_template: '',
})

const configJson = ref('')
const configError = ref('')
const createLoading = ref(false)
const createError = ref('')

const handleCreate = async () => {
  configError.value = ''
  createError.value = ''

  let defaultConfig = undefined
  if (configJson.value.trim()) {
    try {
      defaultConfig = JSON.parse(configJson.value)
    } catch {
      configError.value = 'JSON 格式错误'
      return
    }
  }

  createLoading.value = true
  try {
    await phase3Api.createAgentRole({
      name: form.value.name,
      description: form.value.description || undefined,
      system_prompt_template: form.value.system_prompt_template || undefined,
      default_config: defaultConfig,
    })
    router.push('/agent-roles')
  } catch {
    createError.value = '创建失败'
  } finally {
    createLoading.value = false
  }
}
</script>