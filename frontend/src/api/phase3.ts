import api from './index'
import type { ApiResponse } from '@/types'

// ========== Agent Roles ==========

export interface AgentRole {
  id: string
  name: string
  description: string | null
  system_prompt_template: string | null
  default_config: Record<string, unknown> | null
  org_id: string
  created_at: string
  updated_at: string
}

export interface AgentRoleCreate {
  name: string
  description?: string
  system_prompt_template?: string
  default_config?: Record<string, unknown>
  org_id?: string
}

export interface AgentRoleUpdate {
  name?: string
  description?: string
  system_prompt_template?: string
  default_config?: Record<string, unknown>
}

export const listAgentRoles = () =>
  api.get<ApiResponse<AgentRole[]>>('/agent-roles')

export const createAgentRole = (data: AgentRoleCreate) =>
  api.post<ApiResponse<AgentRole>>('/agent-roles', data)

export const getAgentRole = (id: string) =>
  api.get<ApiResponse<AgentRole>>(`/agent-roles/${id}`)

export const updateAgentRole = (id: string, data: AgentRoleUpdate) =>
  api.put<ApiResponse<AgentRole>>(`/agent-roles/${id}`, data)

export const deleteAgentRole = (id: string) =>
  api.delete<ApiResponse>(`/agent-roles/${id}`)

// ========== Agent Skills ==========

export interface AgentSkill {
  id: string
  agent_id: string
  skill_name: string
  skill_config: Record<string, unknown> | null
  enabled: boolean
  created_at: string
}

export interface AgentSkillBind {
  skill_name: string
  skill_config?: Record<string, unknown>
  enabled?: boolean
}

export const bindAgentSkill = (agentId: string, data: AgentSkillBind) =>
  api.post<ApiResponse<AgentSkill>>(`/agents/${agentId}/skills`, data)

export const listAgentSkills = (agentId: string) =>
  api.get<ApiResponse<AgentSkill[]>>(`/agents/${agentId}/skills`)

export const unbindAgentSkill = (agentId: string, skillId: string) =>
  api.delete<ApiResponse>(`/agents/${agentId}/skills/${skillId}`)

export const updateAgentSkill = (agentId: string, skillId: string, data: { enabled?: boolean; skill_config?: Record<string, unknown> }) =>
  api.put<ApiResponse<AgentSkill>>(`/agents/${agentId}/skills/${skillId}`, data)

// ========== Agent Memory ==========

export interface AgentMemoryConfig {
  agent_id: string
  memory_type: string
  max_context_tokens: number
  context_window: number
  persist_context: boolean
  context_items: number
}

export interface AgentContextRequest {
  context: Record<string, unknown>
}

export interface AgentHistory {
  agent_id: string
  messages: Record<string, unknown>[]
  total: number
}

export const getAgentMemory = (agentId: string) =>
  api.get<ApiResponse<AgentMemoryConfig>>(`/agents/${agentId}/memory`)

export const updateAgentMemory = (agentId: string, data: AgentMemoryConfig) =>
  api.put<ApiResponse<AgentMemoryConfig>>(`/agents/${agentId}/memory`, data)

export const setAgentContext = (agentId: string, data: AgentContextRequest) =>
  api.post<ApiResponse<{ agent_id: string; message: string }>>(`/agents/${agentId}/context`, data)

export const getAgentHistory = (agentId: string, limit = 50) =>
  api.get<ApiResponse<AgentHistory>>(`/agents/${agentId}/history?limit=${limit}`)

export const clearAgentMemory = (agentId: string) =>
  api.delete<ApiResponse<{ agent_id: string; message: string }>>(`/agents/${agentId}/memory/clear`)

export const resetAgentState = (agentId: string) =>
  api.post<ApiResponse<{ agent_id: string; status: string; message: string }>>(`/agents/${agentId}/reset`)

// ========== Agent Metrics ==========

export interface AgentMetric {
  id: string
  agent_id: string
  date: string
  tasks_completed: number
  tasks_failed: number
  avg_response_time_ms: number
  token_usage: number
  created_at: string
}

export interface AgentDailyStats {
  agent_id: string
  date: string
  tasks_completed: number
  tasks_failed: number
  avg_response_time_ms: number
  token_usage: number
}

export interface AgentTaskCount {
  agent_id: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
}

export interface OrgAgentUsage {
  org_id: string
  total_agents: number
  active_agents: number
  total_tasks_completed: number
  total_token_usage: number
  agents: { id: string; name: string; status: string }[]
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

export interface AgentHealthDetail {
  id: string
  healthy: boolean
  status: string
  cpu_percent: number | null
  memory_mb: number | null
  uptime_seconds: number | null
  last_check_at: string
  error_count_today: number
}

export const getAgentMetrics = (agentId: string, days = 7) =>
  api.get<ApiResponse<AgentMetric[]>>(`/agents/${agentId}/metrics?days=${days}`)

export const getAgentDailyStats = (agentId: string, startDate: string, endDate: string) =>
  api.get<ApiResponse<AgentDailyStats[]>>(`/agents/${agentId}/metrics/daily?start_date=${startDate}&end_date=${endDate}`)

export const getAgentTaskCounts = (agentId: string) =>
  api.get<ApiResponse<AgentTaskCount>>(`/agents/${agentId}/tasks/count`)

export const getOrgAgentUsage = (orgId: string) =>
  api.get<ApiResponse<OrgAgentUsage>>(`/orgs/${orgId}/agents/usage`)

export const getAgentPerformance = (agentId: string, days = 7) =>
  api.get<ApiResponse<AgentPerformance>>(`/agents/${agentId}/performance?days=${days}`)

export const getAgentHealthDetail = (agentId: string) =>
  api.get<ApiResponse<AgentHealthDetail>>(`/agents/${agentId}/health`)