import api from './index'
import type { ApiResponse } from '@/types'

export interface SchedulerJob {
  id: string
  name: string
  task_template_id: string
  cron_expression: string
  agent_id: string
  enabled: boolean
  last_run_at?: string
  next_run_at?: string
  created_at: string
}

export interface SchedulerJobCreate {
  name: string
  task_template_id: string
  cron_expression: string
  agent_id: string
  enabled?: boolean
}

export interface SchedulerJobUpdate {
  name?: string
  cron_expression?: string
  agent_id?: string
  enabled?: boolean
}

export interface JobRun {
  execution_id: string
  status: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export const createJob = (data: SchedulerJobCreate) =>
  api.post<ApiResponse<SchedulerJob>>('/scheduler/jobs', data)

export const listJobs = () =>
  api.get<ApiResponse<{ items: SchedulerJob[]; total: number }>>('/scheduler/jobs')

export const getJob = (id: string) =>
  api.get<ApiResponse<SchedulerJob>>(`/scheduler/jobs/${id}`)

export const updateJob = (id: string, data: SchedulerJobUpdate) =>
  api.put<ApiResponse<SchedulerJob>>(`/scheduler/jobs/${id}`, data)

export const deleteJob = (id: string) =>
  api.delete<ApiResponse>(`/scheduler/jobs/${id}`)

export const getJobRuns = (id: string) =>
  api.get<ApiResponse<{ items: JobRun[]; total: number }>>(`/scheduler/jobs/${id}/runs`)
