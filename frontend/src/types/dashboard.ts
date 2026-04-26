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

// Phase 7 Chart types
export interface AgentsTasksChartData {
  labels: string[];
  datasets: {
    agent_id: string;
    agent_name: string;
    data: number[];
  }[];
}

export interface TaskCompletionChartData {
  labels: string[];
  completed: number[];
  failed: number[];
}

export interface ActivityHeatmapData {
  days: string[];
  hours: number[];
  values: number[][];
}