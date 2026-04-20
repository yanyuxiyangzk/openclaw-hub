import api from './index'

export const listOrgs = () => api.get('/orgs')

export const createOrg = (data: { name: string; description?: string }) =>
  api.post('/orgs', data)

export const getOrg = (id: string) => api.get(`/orgs/${id}`)

export const updateOrg = (id: string, data: { name?: string; description?: string }) =>
  api.put(`/orgs/${id}`, data)

export const deleteOrg = (id: string) => api.delete(`/orgs/${id}`)

export const getMembers = (orgId: string) => api.get(`/orgs/${orgId}/members`)

export const removeMember = (orgId: string, userId: string) =>
  api.delete(`/orgs/${orgId}/members/${userId}`)

export const sendInvitation = (orgId: string, data: { email: string; role?: string }) =>
  api.post(`/orgs/${orgId}/invitations`, data)

export const verifyInvitation = (token: string) => api.get(`/invitations/${token}`)

export const acceptInvitation = (token: string) => api.post(`/invitations/${token}/accept`)

export const revokeInvitation = (invId: string) => api.delete(`/invitations/${invId}`)
