<template>
  <div v-if="authStore.isInitialized" id="app">
    <router-view />
  </div>
  <div v-else class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="text-gray-400">Loading...</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initialize()
})
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
