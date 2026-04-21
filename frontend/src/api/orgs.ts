import api from './index'
import type { ApiResponse, Org, OrgMember, Invitation } from '@/types'

export const listOrgs = () => api.get<ApiResponse<Org[]>>('/orgs')

export const createOrg = (data: { name: string }) =>
  api.post<ApiResponse<Org>>('/orgs', data)

export const getOrg = (id: string) => api.get<ApiResponse<Org>>(`/orgs/${id}`)

export const updateOrg = (id: string, data: { name: string }) =>
  api.put<ApiResponse<Org>>(`/orgs/${id}`, data)

export const deleteOrg = (id: string) => api.delete<ApiResponse>(`/orgs/${id}`)

export const getMembers = (orgId: string) =>
  api.get<ApiResponse<{ items: OrgMember[]; total: number }>>(`/orgs/${orgId}/members`)

export const removeMember = (orgId: string, userId: string) =>
  api.delete<ApiResponse>(`/orgs/${orgId}/members/${userId}`)

export const sendInvitation = (orgId: string, data: { email: string; role?: string }) =>
  api.post<ApiResponse<Invitation>>(`/orgs/${orgId}/invitations`, data)

export const verifyInvitation = (token: string) =>
  api.get<ApiResponse<{ valid: boolean; invitation: Invitation | null; organization_name: string | null }>>(`/invitations/${token}`)

export const acceptInvitation = (token: string) =>
  api.post<ApiResponse<{ success: boolean; message: string; organization_id: string | null; organization_name: string | null }>>(`/invitations/${token}/accept`)

export const revokeInvitation = (invId: string) =>
  api.delete<ApiResponse>(`/invitations/${invId}`)
