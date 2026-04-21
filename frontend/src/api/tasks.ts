import api from './index'
import type { ApiResponse } from '@/types'

// ========== Task Types ==========

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
}

export type TaskStatus = 'todo' | 'in_progress' | 'in_review' | 'done' | 'blocked'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface TaskCreate {
  title: string
  description?: string
  project_id: string
  status?: TaskStatus
  priority?: TaskPriority
  parent_id?: string
  root_id?: string
  position?: number
  estimated_hours?: number
  actual_hours?: number
  tags?: string[]
  due_date?: string
  reminder_at?: string
  assignee_id?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  position?: number
  estimated_hours?: number
  actual_hours?: number
  tags?: string[]
  due_date?: string
  reminder_at?: string
  assignee_id?: string
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

// ========== Task APIs ==========

export const createTask = (data: TaskCreate) =>
  api.post<ApiResponse<Task>>('/tasks', data)

export const listTasks = (params?: {
  project_id?: string
  status?: TaskStatus
  assignee_id?: string
  priority?: TaskPriority
}) =>
  api.get<ApiResponse<{ items: Task[]; total: number }>>('/tasks', { params })

export const getTask = (taskId: string) =>
  api.get<ApiResponse<Task>>(`/tasks/${taskId}`)

export const updateTask = (taskId: string, data: TaskUpdate) =>
  api.put<ApiResponse<Task>>(`/tasks/${taskId}`, data)

export const deleteTask = (taskId: string) =>
  api.delete<ApiResponse>(`/tasks/${taskId}`)

export const bulkCreateTasks = (tasks: TaskCreate[]) =>
  api.post<ApiResponse<{ items: Task[]; total: number }>>('/tasks/bulk', { tasks })

export const bulkUpdateStatus = (taskIds: string[], status: TaskStatus) =>
  api.put<ApiResponse<{ items: Task[]; total: number }>>('/tasks/bulk/status', { task_ids: taskIds, status })

export const exportTasks = (projectId: string, format: 'json' | 'csv' = 'json') =>
  api.get<ApiResponse<{ format: string; content: string }>>('/tasks/export', {
    params: { project_id: projectId, format }
  })

// ========== Task Collaboration APIs ==========

export const assignTask = (taskId: string, assigneeId: string) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/assign`, { assignee_id: assigneeId })

export const claimTask = (taskId: string) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/claim`)

export const completeTask = (taskId: string) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/complete`)

export const addComment = (taskId: string, content: string) =>
  api.post<ApiResponse<TaskComment>>(`/tasks/${taskId}/comment`, { content })

export const getComments = (taskId: string) =>
  api.get<ApiResponse<{ items: TaskComment[]; total: number }>>(`/tasks/${taskId}/comments`)

export const createSubtask = (taskId: string, data: TaskCreate) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/subtasks`, data)

export const getSubtasks = (taskId: string) =>
  api.get<ApiResponse<{ items: Task[]; total: number }>>(`/tasks/${taskId}/subtasks`)

export const uploadAttachment = (taskId: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post<ApiResponse<TaskAttachment>>(`/tasks/${taskId}/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getAttachments = (taskId: string) =>
  api.get<ApiResponse<{ items: TaskAttachment[]; total: number }>>(`/tasks/${taskId}/attachments`)

// ========== Kanban View APIs ==========

export const getKanbanBoard = (projectId: string) =>
  api.get<ApiResponse<KanbanBoard>>(`/projects/${projectId}/kanban`)

export const getTasksByStatus = (projectId: string) =>
  api.get<ApiResponse<Record<TaskStatus, Task[]>>>(`/projects/${projectId}/tasks/by-status`)

export const getTasksByAssignee = (projectId: string) =>
  api.get<ApiResponse<Record<string, Task[]>>>(`/projects/${projectId}/tasks/by-assignee`)

export const getTimeline = (projectId: string) =>
  api.get<ApiResponse<Task[]>>(`/projects/${projectId}/tasks/timeline`)

export const moveTask = (taskId: string, data: { status?: TaskStatus; position?: number; assignee_id?: string }) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/move`, data)

export const getActivity = (taskId: string) =>
  api.get<ApiResponse<TaskActivity[]>>(`/tasks/${taskId}/activity`)

// ========== Reminder APIs ==========

export const setReminder = (taskId: string, reminderAt: string) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/remind`, { reminder_at: reminderAt })

export const getDueSoonTasks = (hours: number = 24) =>
  api.get<ApiResponse<DueSoonTasks>>('/tasks/due-soon', { params: { hours } })

export const snoozeReminder = (taskId: string, snoozeMinutes: number) =>
  api.post<ApiResponse<Task>>(`/tasks/${taskId}/snooze`, { snooze_minutes: snoozeMinutes })
