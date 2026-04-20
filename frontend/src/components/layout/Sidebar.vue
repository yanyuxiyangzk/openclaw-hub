<template>
  <aside class="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
    <div class="p-4 border-b border-gray-700">
      <h1 class="text-xl font-bold text-purple-500">OpenClawHub</h1>
    </div>
    <nav class="flex-1 p-4 space-y-2">
      <router-link
        to="/orgs"
        class="block px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition"
        active-class="bg-gray-700 text-white"
      >
        我的组织
      </router-link>
      <router-link
        to="/settings"
        class="block px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition"
        active-class="bg-gray-700 text-white"
      >
        个人设置
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
</script>
