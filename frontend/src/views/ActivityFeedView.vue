<template>
  <div class="activity-feed-view p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900">活动动态</h1>
    </div>
    <ActivityFeed />
  </div>
</template>

<script setup lang="ts">
import ActivityFeed from '../components/activities/ActivityFeed.vue';
</script>
