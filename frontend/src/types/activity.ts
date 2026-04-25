export interface Activity {
  id: string;
  tenant_id: string;
  actor_id: string;
  actor_name: string;
  actor_avatar?: string;
  action_type: 'created' | 'updated' | 'deleted' | 'completed' | 'assigned';
  entity_type: 'task' | 'project' | 'agent' | 'workflow';
  entity_id: string;
  entity_name?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface ActivityListData {
  items: Activity[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ActivityCreateData {
  actor_id: string;
  actor_name: string;
  actor_avatar?: string;
  action_type: string;
  entity_type: string;
  entity_id: string;
  entity_name?: string;
  metadata?: Record<string, any>;
}
