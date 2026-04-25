import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as agentsApi from '@/api/agents'
import { useOrgStore } from './org'
import type { Agent, AgentHealth, AgentLogs, AgentConfig } from '@/types'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const agentHealth = ref<AgentHealth | null>(null)
  const agentLogs = ref<AgentLogs | null>(null)

  const fetchAgents = async () => {
    const res = await agentsApi.listAgents()
    agents.value = res.data.data
  }

  const fetchActiveAgents = async () => {
    const res = await agentsApi.listActiveAgents()
    agents.value = res.data.data
  }

  const createAgent = async (data: { name: string; description?: string; agent_type?: string; config?: AgentConfig }) => {
    const orgStore = useOrgStore()
    const orgId = orgStore.currentOrg?.id
    if (!orgId) {
      throw new Error('No organization selected')
    }
    const res = await agentsApi.createAgent({ ...data, org_id: orgId })
    const newAgent = res.data.data
    agents.value.push(newAgent)
    return newAgent
  }

  const fetchAgent = async (id: string) => {
    const res = await agentsApi.getAgent(id)
    currentAgent.value = res.data.data
    return currentAgent.value
  }

  const updateAgent = async (id: string, data: { name?: string; description?: string; config?: AgentConfig }) => {
    const res = await agentsApi.updateAgent(id, data)
    currentAgent.value = res.data.data
    const idx = agents.value.findIndex(a => a.id === id)
    if (idx !== -1) agents.value[idx] = res.data.data
    return currentAgent.value
  }

  const deleteAgent = async (id: string) => {
    await agentsApi.deleteAgent(id)
    agents.value = agents.value.filter(a => a.id !== id)
    if (currentAgent.value?.id === id) {
      currentAgent.value = null
    }
  }

  const startAgent = async (id: string) => {
    const res = await agentsApi.startAgent(id)
    if (currentAgent.value?.id === id) {
      currentAgent.value.status = res.data.data.status as 'offline' | 'online' | 'busy' | 'error'
    }
    return res.data.data
  }

  const stopAgent = async (id: string) => {
    const res = await agentsApi.stopAgent(id)
    if (currentAgent.value?.id === id) {
      currentAgent.value.status = res.data.data.status as 'offline' | 'online' | 'busy' | 'error'
    }
    return res.data.data
  }

  const fetchHealth = async (id: string) => {
    const res = await agentsApi.getAgentHealth(id)
    agentHealth.value = res.data.data
    return agentHealth.value
  }

  const fetchLogs = async (id: string) => {
    const res = await agentsApi.getAgentLogs(id)
    agentLogs.value = res.data.data
    return agentLogs.value
  }

  const agentConfig = ref<Record<string, unknown> | null>(null)

  const fetchConfig = async (id: string) => {
    const res = await agentsApi.getAgentConfig(id)
    agentConfig.value = res.data.data.config
    return agentConfig.value
  }

  const updateConfig = async (id: string, config: Record<string, unknown>) => {
    const res = await agentsApi.updateAgentConfig(id, config)
    agentConfig.value = res.data.data.config
    return agentConfig.value
  }

  return {
    agents, currentAgent, agentHealth, agentLogs, agentConfig,
    fetchAgents, fetchActiveAgents, createAgent, fetchAgent, updateAgent, deleteAgent,
    startAgent, stopAgent, fetchHealth, fetchLogs, fetchConfig, updateConfig,
  }
})