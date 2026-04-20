<template>
  <div class="min-h-screen bg-gray-900 flex">
    <Sidebar />
    <div class="flex-1 flex flex-col">
      <Topbar />
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
</script>
