import api from './index';
import type { DashboardStats, TaskTrendItem, RecentActivity } from '../types/dashboard';

export const dashboardApi = {
  getStats: () => api.get<{ code: number; data: DashboardStats }>('/dashboard/stats'),
  getTaskTrend: (days = 7) => api.get<{ code: number; data: TaskTrendItem[] }>('/dashboard/task-trend', { params: { days } }),
  getRecentActivities: (limit = 10) => api.get<{ code: number; data: RecentActivity[] }>('/dashboard/recent-activities', { params: { limit } }),
  // Chart APIs (Phase 7)
  getAgentsTasksChart: (days = 7) => api.get<{ code: number; data: { labels: string[]; datasets: { agent_id: string; agent_name: string; data: number[] }[] } }>('/dashboard/chart/agents-tasks', { params: { days } }),
  getTaskCompletionChart: (days = 7) => api.get<{ code: number; data: { labels: string[]; completed: number[]; failed: number[] } }>('/dashboard/chart/task-completion', { params: { days } }),
  getActivityHeatmap: (days = 7) => api.get<{ code: number; data: { days: string[]; hours: number[]; values: number[][] } }>('/dashboard/chart/activity-heatmap', { params: { days } }),
};