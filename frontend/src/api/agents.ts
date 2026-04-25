import api from './index'
import type { ApiResponse } from '@/types'
import type { Agent, AgentConfig } from '@/types'

export interface AgentCreate {
  name: string
  description?: string
  agent_type?: string
  config?: AgentConfig
  org_id: string
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

export interface AgentMemoryConfig {
  memory_type?: string
  max_context_tokens?: number
  context_window?: number
  persist_context?: boolean
}

export interface AgentMemoryResponse {
  agent_id: string
  memory_type: string
  max_context_tokens: number
  context_window: number
  persist_context: boolean
  context_items: number
}

export interface AgentHistoryItem {
  id: string
  tenant_id: string
  actor_id: string
  actor_name: string
  actor_avatar: string | null
  action_type: string
  entity_type: string
  entity_id: string
  entity_name: string | null
  extra_data: Record<string, unknown> | null
  created_at: string
}

export interface AgentHistoryResponse {
  items: AgentHistoryItem[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface AgentContextRequest {
  context: Record<string, unknown>
}

export const getAgentMemory = (id: string) =>
  api.get<ApiResponse<AgentMemoryResponse>>(`/agents/${id}/memory`)

export const updateAgentMemory = (id: string, data: AgentMemoryConfig) =>
  api.put<ApiResponse<AgentMemoryResponse>>(`/agents/${id}/memory`, data)

export const setAgentContext = (id: string, data: AgentContextRequest) =>
  api.post<ApiResponse<{ agent_id: string; context: AgentContextRequest }>>(`/agents/${id}/context`, data)

export const getAgentHistory = (id: string, limit = 50) =>
  api.get<ApiResponse<AgentHistoryResponse>>(`/agents/${id}/history?limit=${limit}`)

export const clearAgentMemory = (id: string) =>
  api.delete<ApiResponse<{ agent_id: string; message: string }>>(`/agents/${id}/memory/clear`)

export const resetAgentState = (id: string) =>
  api.post<ApiResponse<{ agent_id: string; message: string }>>(`/agents/${id}/reset`)

// Phase 3 API methods
export interface AgentSkill {
  id: string
  agent_id: string
  skill_name: string
  skill_config: Record<string, unknown> | null
  enabled: boolean
  created_at: string
}

export interface AgentSkillBindRequest {
  skill_name: string
  skill_config?: Record<string, unknown>
  enabled?: boolean
}

export interface AgentMetricEntry {
  id: string
  agent_id: string
  date: string
  tasks_completed: number
  tasks_failed: number
  avg_response_time_ms: number
  token_usage: number
}

export interface AgentMetricsResponse {
  id: string
  metrics: AgentMetricEntry[]
  total_tasks_completed: number
  total_tasks_failed: number
  avg_response_time_ms: number
  total_token_usage: number
}

export interface AgentPerformance {
  agent_id: string
  period_start: string
  period_end: string
  total_tasks: number
  success_rate: number
  avg_response_time_ms: number
  avg_tokens_per_task: number
  uptime_percent: number
}

export interface AgentTaskCount {
  agent_id: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
}

export interface DailyMetricEntry {
  date: string
  tasks_completed: number
  tasks_failed: number
  avg_response_time_ms: number
  token_usage: number
}

export interface AgentDailyMetrics {
  id: string
  start_date: string
  end_date: string
  daily_metrics: DailyMetricEntry[]
}

export const getAgentSkills = (id: string) =>
  api.get<ApiResponse<AgentSkill[]>>(`/agents/${id}/skills`)

export const bindAgentSkill = (id: string, data: AgentSkillBindRequest) =>
  api.post<ApiResponse<AgentSkill>>(`/agents/${id}/skills`, data)

export const unbindAgentSkill = (agentId: string, skillId: string) =>
  api.delete<ApiResponse<{ message: string }>>(`/agents/${agentId}/skills/${skillId}`)

export const getAgentMetrics = (id: string, days = 7) =>
  api.get<ApiResponse<AgentMetricsResponse>>(`/agents/${id}/metrics?days=${days}`)

export const getAgentDailyMetrics = (id: string, startDate?: string, endDate?: string) => {
  let url = `/agents/${id}/metrics/daily`
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  const queryString = params.toString()
  if (queryString) url += `?${queryString}`
  return api.get<ApiResponse<AgentDailyMetrics>>(url)
}

export const getAgentTaskCounts = (id: string) =>
  api.get<ApiResponse<AgentTaskCount>>(`/agents/${id}/tasks/count`)

export const getAgentPerformance = (id: string, days = 7) =>
  api.get<ApiResponse<AgentPerformance>>(`/agents/${id}/performance?days=${days}`)

export interface AgentConfigResponse {
  id: string
  config: Record<string, unknown> | null
}

export const getAgentConfig = (id: string) =>
  api.get<ApiResponse<AgentConfigResponse>>(`/agents/${id}/config`)

export const updateAgentConfig = (id: string, config: Record<string, unknown>) =>
  api.put<ApiResponse<AgentConfigResponse>>(`/agents/${id}/config`, { config })