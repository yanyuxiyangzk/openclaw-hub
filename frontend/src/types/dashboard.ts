export interface DashboardStats {
  project_count: number;
  task_count: number;
  agent_count: number;
  completed_today: number;
}

export interface TaskTrendItem {
  date: string;
  count: number;
}

export interface RecentActivity {
  id: string;
  actor_name: string;
  action_type: string;
  entity_type: string;
  entity_name?: string;
  created_at: string;
}