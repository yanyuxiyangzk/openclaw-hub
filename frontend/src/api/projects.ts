import api from './index'
import type { ApiResponse } from '@/types'
import type { Project, ProjectMember, Agent } from '@/types'

export interface ProjectCreate {
  name: string
  description?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  status?: string
}

export interface ProjectWithMembers extends Project {
  members: ProjectMember[]
}

export const listProjects = () =>
  api.get<ApiResponse<Project[]>>('/projects')

export const createProject = (data: ProjectCreate) =>
  api.post<ApiResponse<Project>>('/projects', data)

export const getProject = (id: string) =>
  api.get<ApiResponse<ProjectWithMembers>>(`/projects/${id}`)

export const updateProject = (id: string, data: ProjectUpdate) =>
  api.put<ApiResponse<Project>>(`/projects/${id}`, data)

export const deleteProject = (id: string) =>
  api.delete<ApiResponse>(`/projects/${id}`)

export const getProjectMembers = (projectId: string) =>
  api.get<ApiResponse<{ items: ProjectMember[]; total: number }>>(`/projects/${projectId}/members`)

export const addProjectMember = (projectId: string, data: { user_id: string; role?: string }) =>
  api.post<ApiResponse<ProjectMember>>(`/projects/${projectId}/members`, data)

export const removeProjectMember = (projectId: string, userId: string) =>
  api.delete<ApiResponse>(`/projects/${projectId}/members/${userId}`)

export interface ProjectAgent {
  id: string
  project_id: string
  agent_id: string
  assigned_at: string
  agent_name: string
  agent_type: string
  agent_status: string
}

export const getProjectAgents = (projectId: string) =>
  api.get<ApiResponse<{ items: ProjectAgent[]; total: number }>>(`/projects/${projectId}/agents`)

export const getAvailableAgents = (projectId: string) =>
  api.get<ApiResponse<Agent[]>>(`/projects/${projectId}/agents/available`)

export const assignAgentToProject = (projectId: string, data: { agent_id: string }) =>
  api.post<ApiResponse<ProjectAgent>>(`/projects/${projectId}/agents`, data)

export const removeAgentFromProject = (projectId: string, agentId: string) =>
  api.delete<ApiResponse>(`/projects/${projectId}/agents/${agentId}`)