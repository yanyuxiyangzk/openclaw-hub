<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-gray-800">OpenClawHub</h1>
        <div class="flex items-center space-x-4">
          <span class="text-gray-600">CEO: 老赵</span>
          <button class="text-primary hover:underline">退出</button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">我的项目</h2>
        <button
          @click="showCreateDialog = true"
          class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-opacity-90 transition"
        >
          + 创建项目
        </button>
      </div>

      <!-- Project Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="project in projects"
          :key="project.id"
          class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
        >
          <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ project.name }}</h3>
          <p class="text-gray-600 text-sm mb-4">{{ project.description }}</p>
          <div class="flex justify-between items-center">
            <span class="text-xs text-gray-500">
              {{ project.agentCount }} 个 AI 员工
            </span>
            <button
              @click="openProject(project.id)"
              class="text-primary hover:underline text-sm"
            >
              打开 →
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="projects.length === 0"
          class="col-span-full text-center py-12 text-gray-500"
        >
          <p class="mb-4">还没有项目</p>
          <button
            @click="showCreateDialog = true"
            class="text-primary hover:underline"
          >
            创建第一个项目
          </button>
        </div>
      </div>
    </main>

    <!-- Create Project Dialog -->
    <div
      v-if="showCreateDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">创建新项目</h3>
        <form @submit.prevent="createProject">
          <div class="mb-4">
            <label class="block text-gray-700 mb-2">项目名称</label>
            <input
              v-model="newProject.name"
              type="text"
              class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="我的新项目"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 mb-2">项目描述</label>
            <textarea
              v-model="newProject.description"
              class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              rows="3"
              placeholder="项目简介..."
            ></textarea>
          </div>
          <div class="flex justify-end space-x-2">
            <button
              type="button"
              @click="showCreateDialog = false"
              class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-opacity-90"
            >
              创建
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const projects = ref([
  {
    id: '1',
    name: 'OpenClawHub',
    description: '一人公司数字员工 SaaS 平台',
    agentCount: 6
  }
])

const showCreateDialog = ref(false)
const newProject = reactive({
  name: '',
  description: ''
})

const createProject = () => {
  // TODO: 调用 API 创建项目
  console.log('Create project:', newProject)
  showCreateDialog.value = false
  newProject.name = ''
  newProject.description = ''
}

const openProject = (id: string) => {
  router.push(`/projects/${id}/kanban`)
}
</script>
