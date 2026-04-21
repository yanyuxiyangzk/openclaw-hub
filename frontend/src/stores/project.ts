import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as projectsApi from '@/api/projects'
import type { Project, ProjectMember } from '@/types'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const members = ref<ProjectMember[]>([])

  const fetchProjects = async () => {
    const res = await projectsApi.listProjects()
    projects.value = res.data.data
  }

  const createProject = async (data: { name: string; description?: string }) => {
    const res = await projectsApi.createProject(data)
    const newProject = res.data.data
    projects.value.push(newProject)
    return newProject
  }

  const fetchProject = async (id: string) => {
    const res = await projectsApi.getProject(id)
    currentProject.value = res.data.data
    members.value = res.data.data.members || []
    return currentProject.value
  }

  const updateProject = async (id: string, data: { name?: string; description?: string; status?: string }) => {
    const res = await projectsApi.updateProject(id, data)
    currentProject.value = res.data.data
    const idx = projects.value.findIndex(p => p.id === id)
    if (idx !== -1) projects.value[idx] = res.data.data
    return currentProject.value
  }

  const deleteProject = async (id: string) => {
    await projectsApi.deleteProject(id)
    projects.value = projects.value.filter(p => p.id !== id)
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }

  const fetchMembers = async (projectId: string) => {
    const res = await projectsApi.getProjectMembers(projectId)
    members.value = res.data.data.items
  }

  const addMember = async (projectId: string, userId: string, role: string = 'member') => {
    const res = await projectsApi.addProjectMember(projectId, { user_id: userId, role })
    members.value.push(res.data.data)
    return res.data.data
  }

  const removeMember = async (projectId: string, userId: string) => {
    await projectsApi.removeProjectMember(projectId, userId)
    members.value = members.value.filter(m => m.user_id !== userId)
  }

  return {
    projects, currentProject, members,
    fetchProjects, createProject, fetchProject, updateProject, deleteProject,
    fetchMembers, addMember, removeMember,
  }
})