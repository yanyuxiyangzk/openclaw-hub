<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push('/projects')" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">{{ projectStore.currentProject?.name }}</h2>
          <span
            v-if="projectStore.currentProject"
            :class="{
              'bg-green-500/20 text-green-400': projectStore.currentProject.status === 'active',
              'bg-yellow-500/20 text-yellow-400': projectStore.currentProject.status === 'archived',
            }"
            class="px-2 py-1 rounded text-xs font-medium"
          >
            {{ statusText(projectStore.currentProject.status) }}
          </span>
        </div>
        <div class="flex gap-2">
          <button
            @click="showEdit = true"
            class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            编辑
          </button>
          <button
            v-if="isOwner"
            @click="handleDelete"
            class="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition"
          >
            删除
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <template v-else-if="projectStore.currentProject">
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <p class="text-gray-400">{{ projectStore.currentProject.description || '暂无描述' }}</p>
          <p class="text-gray-500 text-sm mt-4">
            创建于 {{ formatDate(projectStore.currentProject.created_at) }}
          </p>
        </div>

        <!-- Members Section -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white">成员</h3>
            <button
              v-if="isAdmin"
              @click="showAddMember = true"
              class="px-3 py-1 text-sm bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
            >
              添加成员
            </button>
          </div>

          <div v-if="projectStore.members.length === 0" class="text-gray-400 text-center py-4">
            暂无成员
          </div>
          <div v-else class="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <table class="w-full">
              <thead class="bg-gray-700/50">
                <tr>
                  <th class="px-4 py-3 text-left text-sm text-gray-400">姓名</th>
                  <th class="px-4 py-3 text-left text-sm text-gray-400">邮箱</th>
                  <th class="px-4 py-3 text-left text-sm text-gray-400">角色</th>
                  <th v-if="isAdmin" class="px-4 py-3 text-right text-sm text-gray-400">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-700">
                <tr v-for="member in projectStore.members" :key="member.id" class="hover:bg-gray-700/30">
                  <td class="px-4 py-3 text-white">{{ member.user_name || '未知' }}</td>
                  <td class="px-4 py-3 text-gray-400">{{ member.user_email || '未知' }}</td>
                  <td class="px-4 py-3">
                    <span
                      :class="{
                        'bg-purple-500/20 text-purple-400': member.role === 'owner',
                        'bg-blue-500/20 text-blue-400': member.role === 'admin',
                        'bg-gray-500/20 text-gray-400': member.role === 'member',
                      }"
                      class="px-2 py-1 rounded text-xs font-medium"
                    >
                      {{ roleText(member.role) }}
                    </span>
                  </td>
                  <td v-if="isAdmin" class="px-4 py-3 text-right">
                    <button
                      v-if="member.role !== 'owner'"
                      @click="handleRemoveMember(member.user_id)"
                      class="text-red-400 hover:text-red-300 text-sm"
                    >
                      移除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Agents Section -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white">Agent</h3>
            <button
              v-if="isAdmin"
              @click="openAssignAgentModal"
              class="px-3 py-1 text-sm bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
            >
              分配 Agent
            </button>
          </div>

          <div v-if="projectAgents.length === 0" class="text-gray-400 text-center py-4">
            暂无分配的 Agent
          </div>
          <div v-else class="grid gap-4">
            <div
              v-for="pa in projectAgents"
              :key="pa.id"
              class="bg-gray-800 rounded-xl p-4 border border-gray-700 flex items-center justify-between"
            >
              <div>
                <h4 class="text-white font-medium">{{ pa.agent_name }}</h4>
                <p class="text-gray-400 text-sm">{{ pa.agent_type }}</p>
              </div>
              <div class="flex items-center gap-3">
                <span
                  :class="{
                    'bg-green-500/20 text-green-400': pa.agent_status === 'online',
                    'bg-yellow-500/20 text-yellow-400': pa.agent_status === 'busy',
                    'bg-red-500/20 text-red-400': pa.agent_status === 'error',
                    'bg-gray-500/20 text-gray-400': pa.agent_status === 'offline',
                  }"
                  class="px-2 py-1 rounded text-xs font-medium"
                >
                  {{ statusText(pa.agent_status) }}
                </span>
                <button
                  v-if="isAdmin"
                  @click="handleRemoveAgent(pa.agent_id)"
                  class="text-red-400 hover:text-red-300 text-sm"
                >
                  移除
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Edit Modal -->
      <div v-if="showEdit" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showEdit = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">编辑项目</h3>
          <form @submit.prevent="handleUpdate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">项目名称</label>
              <input
                v-model="editForm.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">项目描述</label>
              <textarea
                v-model="editForm.description"
                rows="3"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              ></textarea>
            </div>
            <p v-if="updateError" class="mb-4 text-sm text-red-400">{{ updateError }}</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="updateLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ updateLoading ? '保存中...' : '保存' }}
              </button>
              <button
                type="button"
                @click="showEdit = false"
                class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Member Modal -->
      <div v-if="showAddMember" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showAddMember = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">添加成员</h3>
          <form @submit.prevent="handleAddMember">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">用户邮箱</label>
              <input
                v-model="memberEmail"
                type="email"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">角色</label>
              <select
                v-model="memberRole"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="member">成员</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            <p v-if="memberError" class="mb-4 text-sm text-red-400">{{ memberError }}</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="memberLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ memberLoading ? '添加中...' : '添加' }}
              </button>
              <button
                type="button"
                @click="showAddMember = false"
                class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Assign Agent Modal -->
      <div v-if="showAssignAgent" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showAssignAgent = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">分配 Agent</h3>
          <div v-if="availableAgents.length === 0" class="text-gray-400 text-center py-4">
            暂无可分配的 Agent
          </div>
          <div v-else class="space-y-2 max-h-60 overflow-y-auto">
            <div
              v-for="agent in availableAgents"
              :key="agent.id"
              @click="handleAssignAgent(agent.id)"
              class="p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition"
            >
              <span class="text-white">{{ agent.name }}</span>
              <span class="text-gray-400 text-sm ml-2">{{ agent.agent_type }}</span>
            </div>
          </div>
          <div class="mt-4">
            <button
              type="button"
              @click="showAssignAgent = false"
              class="w-full px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { getProjectAgents, getAvailableAgents, removeAgentFromProject, assignAgentToProject } from '@/api/projects'
import type { Agent, ProjectAgent } from '@/types'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()
const loading = ref(false)
const showEdit = ref(false)
const showAddMember = ref(false)
const showAssignAgent = ref(false)

const updateLoading = ref(false)
const updateError = ref('')
const editForm = ref({ name: '', description: '' })

const memberLoading = ref(false)
const memberError = ref('')
const memberEmail = ref('')
const memberRole = ref('member')

const projectAgents = ref<ProjectAgent[]>([])
const availableAgents = ref<Agent[]>([])

const projectId = computed(() => route.params.id as string)

const currentUserId = computed(() => {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.sub
    }
  } catch {}
  return null
})

const isOwner = computed(() => {
  const member = projectStore.members.find(m => m.user_id === currentUserId.value)
  return member?.role === 'owner'
})

const isAdmin = computed(() => {
  const member = projectStore.members.find(m => m.user_id === currentUserId.value)
  return member?.role === 'owner' || member?.role === 'admin'
})

onMounted(async () => {
  loading.value = true
  await projectStore.fetchProject(projectId.value)
  if (projectStore.currentProject) {
    editForm.value = {
      name: projectStore.currentProject.name,
      description: projectStore.currentProject.description || '',
    }
  }
  await loadProjectAgents()
  loading.value = false
})

const loadProjectAgents = async () => {
  const res = await getProjectAgents(projectId.value)
  projectAgents.value = res.data.data.items
}

const openAssignAgentModal = async () => {
  const res = await getAvailableAgents(projectId.value)
  availableAgents.value = res.data.data
  showAssignAgent.value = true
}

const handleUpdate = async () => {
  updateLoading.value = true
  updateError.value = ''
  try {
    await projectStore.updateProject(projectId.value, editForm.value)
    showEdit.value = false
  } catch (e) {
    updateError.value = '更新失败'
  } finally {
    updateLoading.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('确定要删除此项目吗？')) return
  await projectStore.deleteProject(projectId.value)
  router.push('/projects')
}

const handleAddMember = async () => {
  memberLoading.value = true
  memberError.value = ''
  try {
    await projectStore.addMember(projectId.value, memberEmail.value, memberRole.value)
    showAddMember.value = false
    memberEmail.value = ''
    memberRole.value = 'member'
  } catch (e) {
    memberError.value = '添加失败'
  } finally {
    memberLoading.value = false
  }
}

const handleRemoveMember = async (userId: string) => {
  if (!confirm('确定要移除此成员吗？')) return
  await projectStore.removeMember(projectId.value, userId)
}

const handleAssignAgent = async (agentId: string) => {
  await assignAgentToProject(projectId.value, { agent_id: agentId })
  showAssignAgent.value = false
  await loadProjectAgents()
}

const handleRemoveAgent = async (agentId: string) => {
  if (!confirm('确定要从此项目移除此 Agent 吗？')) return
  await removeAgentFromProject(projectId.value, agentId)
  await loadProjectAgents()
}

const statusText = (status: string) => {
  const map: Record<string, string> = {
    active: '进行中',
    archived: '已归档',
    deleted: '已删除',
    online: '在线',
    busy: '忙碌',
    error: '错误',
    offline: '离线',
  }
  return map[status] || status
}

const roleText = (role: string) => {
  const map: Record<string, string> = {
    owner: '所有者',
    admin: '管理员',
    member: '成员',
  }
  return map[role] || role
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>