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

// ========== Phase 3 Types ==========

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

export interface AgentSkill {
  id: string
  agent_id: string
  skill_name: string
  skill_config: Record<string, unknown> | null
  enabled: boolean
  created_at: string
}

export interface AgentMemoryConfig {
  agent_id: string
  memory_type: string
  max_context_tokens: number
  context_window: number
  persist_context: boolean
  context_items: number
}

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

export interface AgentTaskCount {
  agent_id: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
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

export interface AgentHistory {
  items: AgentHistoryItem[]
  total: number
  page: number
  limit: number
  pages: number
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

// ========== Phase 4 Task Types ==========

export type TaskStatus = 'todo' | 'in_progress' | 'in_review' | 'done' | 'blocked'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Task {
  id: string
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  parent_id: string | null
  root_id: string | null
  position: number
  estimated_hours: number | null
  actual_hours: number | null
  tags: string[] | null
  due_date: string | null
  reminder_at: string | null
  started_at: string | null
  completed_at: string | null
  project_id: string
  assignee_id: string | null
  created_by: string
  created_at: string
  updated_at: string
  comment_count?: number
  subtask_count?: number
}

export interface TaskComment {
  id: string
  task_id: string
  user_id: string
  content: string
  created_at: string
  updated_at: string
  author_email: string | null
  author_name: string | null
}

export interface TaskAttachment {
  id: string
  task_id: string
  filename: string
  file_url: string
  file_size: number
  uploaded_by: string
  uploaded_at: string
  uploader_email: string | null
  uploader_name: string | null
}

export interface KanbanColumn {
  status: TaskStatus
  tasks: Task[]
  count: number
}

export interface KanbanBoard {
  columns: KanbanColumn[]
  total: number
}

export interface DueSoonTasks {
  tasks: Task[]
  total: number
  overdue: number
  due_today: number
  due_this_week: number
}

export interface TaskActivity {
  id: string
  task_id: string
  user_id: string
  action: string
  old_value: string | null
  new_value: string | null
  created_at: string
  user_email: string | null
  user_name: string | null
}
