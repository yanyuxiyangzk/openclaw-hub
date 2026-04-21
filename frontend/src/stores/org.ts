import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as orgsApi from '@/api/orgs'
import type { Org, OrgMember } from '@/types'

export const useOrgStore = defineStore('org', () => {
  const orgs = ref<Org[]>([])
  const currentOrg = ref<Org | null>(null)
  const members = ref<OrgMember[]>([])

  const fetchOrgs = async () => {
    const res = await orgsApi.listOrgs()
    orgs.value = res.data.data
  }

  const createOrg = async (name: string) => {
    const res = await orgsApi.createOrg({ name })
    const newOrg = res.data.data
    orgs.value.push(newOrg)
    return newOrg
  }

  const fetchOrg = async (id: string) => {
    const res = await orgsApi.getOrg(id)
    currentOrg.value = res.data.data
    return currentOrg.value
  }

  const updateOrg = async (id: string, payload: { name: string }) => {
    const res = await orgsApi.updateOrg(id, payload)
    currentOrg.value = res.data.data
    const idx = orgs.value.findIndex(o => o.id === id)
    if (idx !== -1) orgs.value[idx] = res.data.data
  }

  const deleteOrg = async (id: string) => {
    await orgsApi.deleteOrg(id)
    orgs.value = orgs.value.filter(o => o.id !== id)
  }

  const fetchMembers = async (orgId: string) => {
    const res = await orgsApi.getMembers(orgId)
    members.value = res.data.data.items
  }

  const removeMember = async (orgId: string, userId: string) => {
    await orgsApi.removeMember(orgId, userId)
    members.value = members.value.filter(m => m.user_id !== userId)
  }

  const inviteMember = async (orgId: string, email: string, role?: string) => {
    await orgsApi.sendInvitation(orgId, { email, role })
  }

  const checkInvitation = async (token: string) => {
    const res = await orgsApi.verifyInvitation(token)
    const d = res.data.data
    return { orgName: d.organization_name, valid: d.valid, invitation: d.invitation }
  }

  const acceptInvite = async (token: string) => {
    await orgsApi.acceptInvitation(token)
  }

  return {
    orgs, currentOrg, members,
    fetchOrgs, createOrg, fetchOrg, updateOrg, deleteOrg,
    fetchMembers, removeMember, inviteMember, checkInvitation, acceptInvite,
  }
})
