<template>
  <div class="activity-item flex gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
    <img v-if="activity.actor_avatar" :src="activity.actor_avatar" class="w-8 h-8 rounded-full" />
    <div v-else class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-sm font-medium">
      {{ activity.actor_name?.charAt(0) || '?' }}
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-sm text-gray-900">
        <span class="font-medium">{{ activity.actor_name }}</span>
        <span class="text-gray-500"> {{ actionText }} </span>
        <span class="font-medium">{{ activity.entity_name || activity.entity_id }}</span>
      </p>
      <p class="text-xs text-gray-400 mt-0.5">{{ formatTime(activity.created_at) }}</p>
    </div>
    <span class="px-2 py-0.5 text-xs rounded-full" :class="actionBadgeClass">{{ activity.action_type }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Activity } from '../../types/activity';

const props = defineProps<{ activity: Activity }>();

const actionText = computed(() => ({
  created: '创建了',
  updated: '更新了',
  deleted: '删除了',
  completed: '完成了',
  assigned: '分配了',
}[props.activity.action_type] || '操作了'));

const actionBadgeClass = computed(() => ({
  created: 'bg-green-100 text-green-700',
  updated: 'bg-blue-100 text-blue-700',
  deleted: 'bg-red-100 text-red-700',
  completed: 'bg-purple-100 text-purple-700',
  assigned: 'bg-yellow-100 text-yellow-700',
}[props.activity.action_type] || 'bg-gray-100 text-gray-700'));

function formatTime(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return '刚刚';
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  return d.toLocaleDateString('zh-CN');
}
</script>
