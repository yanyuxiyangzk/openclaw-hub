export interface User {
  id: string
  name: string
  email: string
  avatar: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface Org {
  id: string
  name: string
  owner_id: string
  created_at: string
  updated_at: string
}

export interface OrgMember {
  id: string
  org_id: string
  user_id: string
  role: string
  joined_at: string
  user_email: string | null
  user_name: string | null
}

export interface Invitation {
  id: string
  org_id: string
  email: string
  role: string
  token: string
  expires_at: string
  status: string
  created_at: string
}

export interface Project {
  id: string
  name: string
  description: string | null
  org_id: string
  status: 'active' | 'archived' | 'deleted'
  settings: string | null
  created_by: string
  created_at: string
  updated_at: string
}

export interface ProjectMember {
  id: string
  project_id: string
  user_id: string
  role: 'owner' | 'admin' | 'member'
  joined_at: string
  user_email: string | null
  user_name: string | null
}

export interface ProjectAgent {
  id: string
  project_id: string
  agent_id: string
  assigned_at: string
  agent_name: string
  agent_type: string
  agent_status: string
}

export interface AgentConfig {
  model?: string
  temperature?: number
  max_tokens?: number
  system_prompt?: string
  [key: string]: unknown
}

export interface Agent {
  id: string
  name: string
  description: string | null
  agent_type: string
  config: AgentConfig | null
  org_id: string
  status: 'offline' | 'online' | 'busy' | 'error'
  created_at: string
  updated_at: string
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

export interface AgentHealth {
  id: string
  healthy: boolean
  cpu_percent: number | null
  memory_mb: number | null
  uptime_seconds: number | null
  last_check_at: string
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
