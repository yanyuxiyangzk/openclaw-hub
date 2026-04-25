<template>
  <div class="activity-feed">
    <ActivityItem v-for="item in activities" :key="item.id" :activity="item" />
    <div v-if="loading" class="text-center py-4 text-gray-400 text-sm">加载中...</div>
    <div v-else-if="activities.length === 0" class="text-center py-8 text-gray-400 text-sm">暂无动态</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import ActivityItem from './ActivityItem.vue';
import { activitiesApi } from '../../api/activities';
import type { Activity } from '../../types/activity';

const activities = ref<Activity[]>([]);
const loading = ref(false);

const props = withDefaults(defineProps<{
  actor_id?: string;
  action_type?: string;
  entity_type?: string;
  limit?: number;
}>(), {
  limit: 20,
});

async function fetchActivities() {
  loading.value = true;
  try {
    const { data } = await activitiesApi.list({ page: 1, limit: props.limit, actor_id: props.actor_id, action_type: props.action_type, entity_type: props.entity_type });
    activities.value = data.data.items;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchActivities);
defineExpose({ refetch: fetchActivities });
</script>
