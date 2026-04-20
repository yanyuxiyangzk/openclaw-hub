<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-white">我的组织</h2>
        <button
          @click="showCreate = true"
          class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          创建组织
        </button>
      </div>

      <div v-if="loading" class="text-gray-400">加载中...</div>
      <div v-else-if="orgStore.orgs.length === 0" class="text-gray-400 text-center py-8">
        暂无组织，点击上方按钮创建
      </div>
      <div v-else class="grid gap-4">
        <div
          v-for="org in orgStore.orgs"
          :key="org.id"
          class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-purple-500 transition cursor-pointer"
          @click="router.push(`/orgs/${org.id}`)"
        >
          <h3 class="text-lg font-semibold text-white">{{ org.name }}</h3>
          <p class="text-gray-400 text-sm mt-1">{{ org.description || '暂无描述' }}</p>
        </div>
      </div>

      <!-- Create Modal -->
      <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center" @click.self="showCreate = false">
        <div class="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">创建组织</h3>
          <form @submit.prevent="handleCreate">
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">组织名称</label>
              <input
                v-model="newOrg.name"
                type="text"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-400 mb-2 text-sm">描述 (可选)</label>
              <textarea
                v-model="newOrg.description"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows="3"
              ></textarea>
            </div>
            <p v-if="createError" class="mb-4 text-sm text-red-400">{{ createError }}</p>
            <div class="flex gap-3">
              <button
                type="submit"
                :disabled="createLoading"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                {{ createLoading ? '创建中...' : '创建' }}
              </button>
              <button
                type="button"
                @click="showCreate = false"
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
import { useRouter } from 'vue-router'
import { useOrgStore } from '@/stores/org'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = useRouter()
const orgStore = useOrgStore()
const loading = ref(false)
const showCreate = ref(false)
const createLoading = ref(false)
const createError = ref('')
const newOrg = ref({ name: '', description: '' })

onMounted(async () => {
  loading.value = true
  await orgStore.fetchOrgs()
  loading.value = false
})

const handleCreate = async () => {
  createLoading.value = true
  createError.value = ''
  try {
    await orgStore.createOrg(newOrg.value.name, newOrg.value.description)
    showCreate.value = false
    newOrg.value = { name: '', description: '' }
  } catch (e) {
    createError.value = '创建失败'
  } finally {
    createLoading.value = false
  }
}
</script>
