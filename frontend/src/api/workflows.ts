import api from './index'
import type { ApiResponse } from '@/types'
import type { Execution } from './executions'

export interface WorkflowStep {
  step_id: string
  name: string
  task_template_id: string
  agent_id: string
  depends_on: string[]
  config?: Record<string, any>
}

export interface Workflow {
  id: string
  name: string
  description?: string
  steps: WorkflowStep[]
  org_id: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface WorkflowCreate {
  name: string
  description?: string
  steps: WorkflowStep[]
}

export interface WorkflowUpdate {
  name?: string
  description?: string
  steps?: WorkflowStep[]
}

export interface WorkflowExecuteRequest {
  input_data?: Record<string, any>
  agent_id?: string
}

export const createWorkflow = (data: WorkflowCreate) =>
  api.post<ApiResponse<Workflow>>('/workflows', data)

export const listWorkflows = (orgId?: string) =>
  api.get<ApiResponse<{ items: Workflow[]; total: number }>>('/workflows', { params: { org_id: orgId } })

export const getWorkflow = (id: string) =>
  api.get<ApiResponse<Workflow>>(`/workflows/${id}`)

export const updateWorkflow = (id: string, data: WorkflowUpdate) =>
  api.put<ApiResponse<Workflow>>(`/workflows/${id}`, data)

export const deleteWorkflow = (id: string) =>
  api.delete<ApiResponse>(`/workflows/${id}`)

export const executeWorkflow = (id: string, data: WorkflowExecuteRequest) =>
  api.post<ApiResponse<{ items: Execution[]; total: number }>>(`/workflows/${id}/execute`, data)
