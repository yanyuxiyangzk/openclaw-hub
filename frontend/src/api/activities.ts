import api from './index';
import type { Activity, ActivityListData, ActivityCreateData } from '../types/activity';

export const activitiesApi = {
  list: (params: { page?: number; limit?: number; actor_id?: string; action_type?: string; entity_type?: string }) => {
    return api.get<{ code: number; data: ActivityListData }>('/activities', { params });
  },
  create: (data: ActivityCreateData) => {
    return api.post<{ code: number; data: Activity }>('/activities', data);
  },
  unreadCount: () => {
    return api.get<{ code: number; data: { unread_count: number } }>('/activities/unread');
  },
  markAsRead: (activityIds?: string[]) => {
    return api.post<{ code: number; data: { marked_count: number } }>('/activities/mark-read', activityIds);
  },
};
