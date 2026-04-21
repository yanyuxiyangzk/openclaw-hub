import api from './index'
import type { ApiResponse } from '@/types'
import type { Agent, AgentConfig } from '@/types'

export interface AgentCreate {
  name: string
  description?: string
  agent_type?: string
  config?: AgentConfig
}

export interface AgentUpdate {
  name?: string
  description?: string
  config?: AgentConfig
}

export interface AgentStatus {
  id: string
  status: string
}

export interface AgentHealth {
  id: string
  healthy: boolean
  cpu_percent: number | null
  memory_mb: number | null
  uptime_seconds: number | null
  last_check_at: string
}

export interface AgentLogEntry {
  timestamp: string
  level: string
  message: string
}

export interface AgentLogs {
  id: string
  logs: AgentLogEntry[]
  total: number
}

export const listAgents = () =>
  api.get<ApiResponse<Agent[]>>('/agents')

export const listActiveAgents = () =>
  api.get<ApiResponse<Agent[]>>('/agents/active')

export const createAgent = (data: AgentCreate) =>
  api.post<ApiResponse<Agent>>('/agents', data)

export const getAgent = (id: string) =>
  api.get<ApiResponse<Agent>>(`/agents/${id}`)

export const updateAgent = (id: string, data: AgentUpdate) =>
  api.put<ApiResponse<Agent>>(`/agents/${id}`, data)

export const deleteAgent = (id: string) =>
  api.delete<ApiResponse>(`/agents/${id}`)

export const getAgentStatus = (id: string) =>
  api.get<ApiResponse<AgentStatus>>(`/agents/${id}/status`)

export const startAgent = (id: string) =>
  api.post<ApiResponse<{ id: string; status: string; message: string }>>(`/agents/${id}/start`)

export const stopAgent = (id: string) =>
  api.post<ApiResponse<{ id: string; status: string; message: string }>>(`/agents/${id}/stop`)

export const getAgentLogs = (id: string) =>
  api.get<ApiResponse<AgentLogs>>(`/agents/${id}/logs`)

export const getAgentHealth = (id: string) =>
  api.get<ApiResponse<AgentHealth>>(`/agents/${id}/health`)