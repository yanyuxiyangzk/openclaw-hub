<template>
  <AppLayout>
    <div class="max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="router.push(`/projects/${projectId}`)" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-2xl font-bold text-white">{{ projectStore.currentProject?.name }} — 活动动态</h2>
        </div>
        <button
          @click="markAllRead"
          :disabled="loading"
          class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition disabled:opacity-50"
        >
          全部已读
        </button>
      </div>

      <div class="mb-4 flex gap-2">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="activeFilter = filter.value"
          :class="activeFilter === filter.value
            ? 'bg-purple-500 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-white'"
          class="px-3 py-1.5 rounded-lg text-sm transition"
        >
          {{ filter.label }}
        </button>
      </div>

      <div v-if="loading && !activities.length" class="text-gray-400 py-8 text-center">
        加载中...
      </div>
      <div v-else-if="!activities.length" class="text-gray-400 text-center py-12">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
        </svg>
        <p>暂无活动动态</p>
      </div>
      <div v-else class="space-y-3">
        <ActivityItem
          v-for="activity in activities"
          :key="activity.id"
          :activity="activity"
          @click="handleActivityClick"
        />
        <div v-if="hasMore" class="text-center pt-4">
          <button
            @click="loadMore"
            :disabled="loading"
            class="px-6 py-2 bg-gray-800 text-gray-400 rounded-lg hover:text-white transition disabled:opacity-50"
          >
            {{ loading ? '加载中...' : '加载更多' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import ActivityItem from '@/components/activities/ActivityItem.vue'
import { useProjectStore } from '@/stores/project'
import { activitiesApi } from '@/api/activities'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string
const projectStore = useProjectStore()

const activities = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
const activeFilter = ref('')

const filters = [
  { label: '全部', value: '' },
  { label: '任务', value: 'task' },
  { label: '执行', value: 'execution' },
  { label: 'Agent', value: 'agent' },
]

onMounted(async () => {
  await projectStore.fetchProject(projectId)
  await fetchActivities(true)
})

const fetchActivities = async (reset = false) => {
  if (reset) {
    page.value = 1
    activities.value = []
  }
  loading.value = true
  try {
    const params: any = { page: page.value, limit: 20 }
    if (activeFilter.value) params.entity_type = activeFilter.value
    if (projectId) params.project_id = projectId
    const res = await activitiesApi.list(params)
    const items = res.data.data.items || []
    if (reset) {
      activities.value = items
    } else {
      activities.value.push(...items)
    }
    hasMore.value = items.length === 20
  } catch (e) {
    console.error('Failed to fetch activities:', e)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchActivities(false)
}

const markAllRead = async () => {
  try {
    await activitiesApi.markAsRead()
    activities.value.forEach(a => { a.read_at = new Date().toISOString() })
  } catch (e) {
    console.error('Failed to mark all read:', e)
  }
}

const handleActivityClick = (activity: any) => {
  if (activity.entity_type === 'task' && activity.entity_id) {
    router.push(`/tasks/${activity.entity_id}`)
  } else if (activity.entity_type === 'execution' && activity.entity_id) {
    router.push(`/executions/${activity.entity_id}`)
  } else if (activity.entity_type === 'agent' && activity.entity_id) {
    router.push(`/agents/${activity.entity_id}`)
  }
}
</script>
