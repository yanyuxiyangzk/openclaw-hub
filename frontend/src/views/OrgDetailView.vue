<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-bold text-white">{{ orgStore.currentOrg?.name }}</h2>
          <p class="text-gray-400 text-sm mt-1">组织详情</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="router.push(`/orgs/${route.params.id}/members`)"
            class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            成员管理
          </button>
          <button
            @click="showEdit = true"
            class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
          >
            编辑组织
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="!orgStore.currentOrg" class="text-gray-400 text-center py-8">
        组织不存在
      </div>
      <div v-else class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-gray-400 text-sm">组织名称</span>
            <p class="text-white mt-1">{{ orgStore.currentOrg.name }}</p>
          </div>
          <div>
            <span class="text-gray-400 text-sm">创建时间</span>
            <p class="text-white mt-1">{{ orgStore.currentOrg.created_at || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="showEdit" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showEdit = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">编辑组织</h3>
          <form @submit.prevent="handleUpdate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">组织名称</label>
              <input
                v-model="editForm.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
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
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrgStore } from '@/stores/org'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const orgStore = useOrgStore()
const loading = ref(false)
const showEdit = ref(false)
const updateLoading = ref(false)
const updateError = ref('')
const editForm = ref({ name: '' })

onMounted(async () => {
  loading.value = true
  await orgStore.fetchOrg(String(route.params.id))
  if (orgStore.currentOrg) {
    editForm.value = { name: orgStore.currentOrg.name }
  }
  loading.value = false
})

const handleUpdate = async () => {
  updateLoading.value = true
  updateError.value = ''
  try {
    await orgStore.updateOrg(String(route.params.id), { name: editForm.value.name })
    showEdit.value = false
  } catch (e) {
    updateError.value = '保存失败'
  } finally {
    updateLoading.value = false
  }
}
</script>
