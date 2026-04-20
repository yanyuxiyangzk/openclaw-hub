import { defineStore } from 'pinia'
import { ref } from 'vue'
import { mockOrgs, mockMembers, mockInvitation } from '@/utils/mock'
import type { Org, OrgMember } from '@/types'

export const useOrgStore = defineStore('org', () => {
  const orgs = ref<Org[]>([])
  const currentOrg = ref<Org | null>(null)
  const members = ref<OrgMember[]>([])

  const fetchOrgs = async () => {
    await new Promise(resolve => setTimeout(resolve, 300))
    orgs.value = mockOrgs
  }

  const createOrg = async (name: string, description?: string) => {
    await new Promise(resolve => setTimeout(resolve, 300))
    const newOrg: Org = { id: String(Date.now()), name, description, ownerId: '1' }
    orgs.value.push(newOrg)
    return newOrg
  }

  const fetchOrg = async (id: string) => {
    await new Promise(resolve => setTimeout(resolve, 300))
    currentOrg.value = mockOrgs.find(o => o.id === id) || null
    return currentOrg.value
  }

  const updateOrg = async (id: string, payload: { name?: string; description?: string }) => {
    await new Promise(resolve => setTimeout(resolve, 300))
    const org = mockOrgs.find(o => o.id === id)
    if (org) {
      Object.assign(org, payload)
      currentOrg.value = { ...org }
    }
    const idx = orgs.value.findIndex(o => o.id === id)
    if (idx !== -1) orgs.value[idx] = { ...orgs.value[idx], ...payload }
  }

  const deleteOrg = async (id: string) => {
    await new Promise(resolve => setTimeout(resolve, 200))
    orgs.value = orgs.value.filter(o => o.id !== id)
  }

  const fetchMembers = async (_orgId: string) => {
    await new Promise(resolve => setTimeout(resolve, 300))
    members.value = mockMembers
  }

  const removeMember = async (_orgId: string, userId: string) => {
    await new Promise(resolve => setTimeout(resolve, 200))
    members.value = members.value.filter(m => m.userId !== userId)
  }

  const inviteMember = async (_orgId: string, _email: string, _role?: string) => {
    await new Promise(resolve => setTimeout(resolve, 300))
  }

  const checkInvitation = async (_token: string) => {
    await new Promise(resolve => setTimeout(resolve, 300))
    return mockInvitation
  }

  const acceptInvite = async (_token: string) => {
    await new Promise(resolve => setTimeout(resolve, 300))
  }

  return {
    orgs,
    currentOrg,
    members,
    fetchOrgs,
    createOrg,
    fetchOrg,
    updateOrg,
    deleteOrg,
    fetchMembers,
    removeMember,
    inviteMember,
    checkInvitation,
    acceptInvite,
  }
})
