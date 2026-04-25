import api from './index';
import type { DashboardStats, TaskTrendItem, RecentActivity } from '../types/dashboard';

export const dashboardApi = {
  getStats: () => api.get<{ code: number; data: DashboardStats }>('/dashboard/stats'),
  getTaskTrend: (days = 7) => api.get<{ code: number; data: TaskTrendItem[] }>('/dashboard/task-trend', { params: { days } }),
  getRecentActivities: (limit = 10) => api.get<{ code: number; data: RecentActivity[] }>('/dashboard/recent-activities', { params: { limit } }),
};