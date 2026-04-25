<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push(`/agents/${agentId}`)" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">Agent 配置</h2>
        </div>
      </div>

      <!-- Agent Config Section -->
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Agent 配置</h3>
          <button
            @click="handleSaveConfig"
            :disabled="savingConfig"
            class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 transition"
          >
            {{ savingConfig ? '保存中...' : '保存配置' }}
          </button>
        </div>

        <div v-if="loadingConfig" class="text-gray-400">加载中...</div>
        <div v-else>
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">model</label>
            <input
              v-model="configForm.model"
              type="text"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="例如: hermes-3-llama-3-8b"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">temperature</label>
            <input
              v-model.number="configForm.temperature"
              type="number"
              step="0.1"
              min="0"
              max="2"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="0.0 - 2.0"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">max_tokens</label>
            <input
              v-model.number="configForm.max_tokens"
              type="number"
              min="1"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="最大token数"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-400 mb-2 text-sm">system_prompt</label>
            <textarea
              v-model="configForm.system_prompt"
              rows="4"
              class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              placeholder="系统提示词..."
            />
          </div>
          <p v-if="configError" class="text-sm text-red-400">{{ configError }}</p>
          <p v-if="configSuccess" class="text-sm text-green-400">配置已保存</p>
        </div>
      </div>

      <!-- Skills Section -->
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">技能绑定</h3>
          <button
            @click="showBindSkill = true"
            class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
          >
            绑定技能
          </button>
        </div>

        <div v-if="loadingSkills" class="text-gray-400">加载中...</div>
        <div v-else-if="skills.length === 0" class="text-gray-400 text-center py-4">
          暂无绑定的技能
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="skill in skills"
            :key="skill.id"
            class="flex items-center justify-between bg-gray-700 rounded-lg p-4"
          >
            <div>
              <div class="text-white font-medium">{{ skill.skill_name }}</div>
              <div class="text-gray-400 text-sm">
                {{ skill.enabled ? '已启用' : '已禁用' }}
                · 创建于 {{ formatDate(skill.created_at) }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="toggleSkill(skill)"
                :class="skill.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'"
                class="px-3 py-1 rounded text-sm hover:opacity-80 transition"
              >
                {{ skill.enabled ? '启用' : '禁用' }}
              </button>
              <button
                @click="handleUnbindSkill(skill)"
                class="bg-red-500/20 text-red-400 px-3 py-1 rounded text-sm hover:bg-red-500/30 transition"
              >
                解绑
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent Roles Section -->
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">角色模板</h3>
          <button
            @click="router.push('/agent-roles/new')"
            class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            创建角色
          </button>
        </div>

        <div v-if="loadingRoles" class="text-gray-400">加载中...</div>
        <div v-else-if="roles.length === 0" class="text-gray-400 text-center py-4">
          暂无角色模板
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="role in roles"
            :key="role.id"
            class="flex items-center justify-between bg-gray-700 rounded-lg p-4"
          >
            <div>
              <div class="text-white font-medium">{{ role.name }}</div>
              <div class="text-gray-400 text-sm">
                {{ role.description || '暂无描述' }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="router.push(`/agent-roles/${role.id}`)"
                class="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-500 transition"
              >
                查看
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Bind Skill Modal -->
      <div v-if="showBindSkill" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showBindSkill = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">绑定技能</h3>
          <form @submit.prevent="handleBindSkill">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">技能名称</label>
              <input
                v-model="bindSkillForm.skill_name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="例如: code_assistant, data_analyst"
                required
              />
            </div>
            <div class="mb-4">
              <label class="flex items-center gap-2 text-gray-400">
                <input v-model="bindSkillForm.enabled" type="checkbox" class="rounded" />
                立即启用
              </label>
            </div>
            <p v-if="bindError" class="mb-4 text-sm text-red-400">{{ bindError }}</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="bindLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ bindLoading ? '绑定中...' : '绑定' }}
              </button>
              <button
                type="button"
                @click="showBindSkill = false"
                class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import * as phase3Api from '@/api/phase3'
import { getAgentConfig, updateAgentConfig } from '@/api/agents'
import type { AgentSkill, AgentRole } from '@/types'

const router = useRouter()
const route = useRoute()
const agentId = route.params.id as string

const skills = ref<AgentSkill[]>([])
const roles = ref<AgentRole[]>([])
const loadingSkills = ref(false)
const loadingRoles = ref(false)
const loadingConfig = ref(false)
const savingConfig = ref(false)
const configError = ref('')
const configSuccess = ref(false)
const showBindSkill = ref(false)
const bindLoading = ref(false)
const bindError = ref('')
const bindSkillForm = ref({ skill_name: '', enabled: true })

const configForm = reactive({
  model: '',
  temperature: 0.7,
  max_tokens: 2048,
  system_prompt: '',
})

onMounted(async () => {
  await loadConfig()
  await loadSkills()
  await loadRoles()
})

const loadConfig = async () => {
  loadingConfig.value = true
  configError.value = ''
  try {
    const res = await getAgentConfig(agentId)
    const config = res.data.data.config
    if (config) {
      configForm.model = (config.model as string) || ''
      configForm.temperature = (config.temperature as number) || 0.7
      configForm.max_tokens = (config.max_tokens as number) || 2048
      configForm.system_prompt = (config.system_prompt as string) || ''
    }
  } catch {
    configError.value = '加载配置失败'
  } finally {
    loadingConfig.value = false
  }
}

const handleSaveConfig = async () => {
  savingConfig.value = true
  configError.value = ''
  configSuccess.value = false
  try {
    const config: Record<string, unknown> = {}
    if (configForm.model) config.model = configForm.model
    if (configForm.temperature !== undefined) config.temperature = configForm.temperature
    if (configForm.max_tokens !== undefined) config.max_tokens = configForm.max_tokens
    if (configForm.system_prompt) config.system_prompt = configForm.system_prompt
    await updateAgentConfig(agentId, config)
    configSuccess.value = true
    setTimeout(() => { configSuccess.value = false }, 3000)
  } catch {
    configError.value = '保存配置失败'
  } finally {
    savingConfig.value = false
  }
}

const loadSkills = async () => {
  loadingSkills.value = true
  try {
    const res = await phase3Api.listAgentSkills(agentId)
    skills.value = res.data.data
  } catch {
    skills.value = []
  } finally {
    loadingSkills.value = false
  }
}

const loadRoles = async () => {
  loadingRoles.value = true
  try {
    const res = await phase3Api.listAgentRoles()
    roles.value = res.data.data
  } catch {
    roles.value = []
  } finally {
    loadingRoles.value = false
  }
}

const handleBindSkill = async () => {
  bindLoading.value = true
  bindError.value = ''
  try {
    await phase3Api.bindAgentSkill(agentId, bindSkillForm.value)
    showBindSkill.value = false
    bindSkillForm.value = { skill_name: '', enabled: true }
    await loadSkills()
  } catch {
    bindError.value = '绑定失败'
  } finally {
    bindLoading.value = false
  }
}

const toggleSkill = async (skill: AgentSkill) => {
  try {
    await phase3Api.updateAgentSkill(agentId, skill.id, { enabled: !skill.enabled })
    await loadSkills()
  } catch {}
}

const handleUnbindSkill = async (skill: AgentSkill) => {
  if (!confirm(`确定要解绑技能 "${skill.skill_name}" 吗？`)) return
  try {
    await phase3Api.unbindAgentSkill(agentId, skill.id)
    await loadSkills()
  } catch {}
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>