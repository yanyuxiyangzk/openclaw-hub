import api from './index'
import type { ApiResponse } from '@/types'

export interface Execution {
  id: string
  task_id: string
  agent_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface ExecutionCreate {
  task_id: string
  agent_id: string
  input_data?: Record<string, any>
}

export interface BatchExecuteRequest {
  task_ids: string[]
  agent_id: string
}

export const triggerExecution = (taskId: string, data: ExecutionCreate) =>
  api.post<ApiResponse<Execution>>(`/tasks/${taskId}/execute`, data)

export const batchExecute = (taskId: string, data: BatchExecuteRequest) =>
  api.post<ApiResponse<{ items: Execution[]; total: number }>>(`/tasks/${taskId}/execute/batch`, data)

export const getExecution = (id: string) =>
  api.get<ApiResponse<Execution>>(`/executions/${id}`)

export const getTaskExecutions = (taskId: string) =>
  api.get<ApiResponse<{ items: Execution[]; total: number }>>(`/tasks/${taskId}/executions`)

export const cancelExecution = (id: string) =>
  api.post<ApiResponse<Execution>>(`/executions/${id}/cancel`)

export const retryExecution = (id: string) =>
  api.post<ApiResponse<Execution>>(`/executions/${id}/retry`)

export const getExecutionOutput = (id: string) =>
  api.get<ApiResponse<{ id: string; output_data?: Record<string, any>; status: string }>>(`/executions/${id}/output`)

export const getActiveExecutions = () =>
  api.get<ApiResponse<{ items: Execution[]; total: number }>>(`/executions/active`)
