<template>
  <div class="dashboard-view p-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">数据概览</h1>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <div class="text-gray-500 text-sm">项目数</div>
        <div class="text-3xl font-bold text-primary-600 mt-1">{{ stats.project_count }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <div class="text-gray-500 text-sm">进行中任务</div>
        <div class="text-3xl font-bold text-blue-600 mt-1">{{ stats.task_count }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <div class="text-gray-500 text-sm">数字员工</div>
        <div class="text-3xl font-bold text-purple-600 mt-1">{{ stats.agent_count }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <div class="text-gray-500 text-sm">今日完成</div>
        <div class="text-3xl font-bold text-green-600 mt-1">{{ stats.completed_today }}</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <h2 class="font-semibold text-gray-900 mb-4">任务完成趋势（7天）</h2>
        <div v-if="trend.length" class="flex items-end gap-2 h-40">
          <div v-for="item in trend" :key="item.date" class="flex-1 flex flex-col items-center">
            <div class="w-full bg-primary-500 rounded-t" :style="{ height: `${(item.count / maxTrend) * 100}%` }"></div>
            <div class="text-xs text-gray-400 mt-1">{{ item.date.slice(5) }}</div>
          </div>
        </div>
        <div v-else class="h-40 flex items-center justify-center text-gray-400">暂无数据</div>
      </div>

      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <h2 class="font-semibold text-gray-900 mb-4">最近活动</h2>
        <div class="space-y-2 max-h-40 overflow-y-auto">
          <div v-for="a in recentActivities" :key="a.id" class="text-sm py-1 border-b border-gray-100 last:border-0">
            <span class="font-medium">{{ a.actor_name }}</span>
            <span class="text-gray-500"> {{ actionText(a.action_type) }} </span>
            <span>{{ a.entity_name || a.entity_type }}</span>
          </div>
          <div v-if="!recentActivities.length" class="text-gray-400 text-sm">暂无活动</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { dashboardApi } from '../api/dashboard';

const stats = ref({ project_count: 0, task_count: 0, agent_count: 0, completed_today: 0 });
const trend = ref<{ date: string; count: number }[]>([]);
const recentActivities = ref<any[]>([]);

const maxTrend = computed(() => Math.max(...trend.value.map(t => t.count), 1));

function actionText(type: string) {
  return { created: '创建了', updated: '更新了', completed: '完成了', deleted: '删除了', assigned: '分配了' }[type] || '操作了';
}

onMounted(async () => {
  const [statsRes, trendRes, activitiesRes] = await Promise.all([
    dashboardApi.getStats(),
    dashboardApi.getTaskTrend(7),
    dashboardApi.getRecentActivities(10),
  ]);
  stats.value = statsRes.data.data;
  trend.value = trendRes.data.data;
  recentActivities.value = activitiesRes.data.data;
});
</script>