from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Any


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    agent_type: str = Field(default="hermes", max_length=32)
    config: dict | None = None
    org_id: str


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    description: str | None = None
    config: dict | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str | None
    agent_type: str
    config: dict | None
    org_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentStatusResponse(BaseModel):
    id: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class AgentProjectAssignRequest(BaseModel):
    project_id: str


class ProjectAgentResponse(BaseModel):
    id: str
    project_id: str
    agent_id: str
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentWithProjectsResponse(BaseModel):
    id: str
    name: str
    description: str | None
    agent_type: str
    config: dict | None
    org_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    projects: list[ProjectAgentResponse]

    model_config = ConfigDict(from_attributes=True)


class AgentStartResponse(BaseModel):
    id: str
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class AgentStopResponse(BaseModel):
    id: str
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class AgentHealthResponse(BaseModel):
    id: str
    healthy: bool
    cpu_percent: float | None
    memory_mb: float | None
    uptime_seconds: int | None
    last_check_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentLogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str


class AgentLogsResponse(BaseModel):
    id: str
    logs: list[AgentLogEntry]
    total: int

    model_config = ConfigDict(from_attributes=True)


class ActivityEntry(BaseModel):
    id: str
    tenant_id: str
    actor_id: str
    actor_name: str
    actor_avatar: Optional[str]
    action_type: str
    entity_type: str
    entity_id: str
    entity_name: Optional[str]
    extra_data: Optional[Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentHistoryResponse(BaseModel):
    items: list[ActivityEntry]
    total: int
    page: int
    limit: int
    pages: int


class AgentConfigResponse(BaseModel):
    id: str
    config: dict | None

    model_config = ConfigDict(from_attributes=True)


class AgentConfigUpdate(BaseModel):
    config: dict | None


class AgentMemoryUpdate(BaseModel):
    memory_type: str = Field(default="shortterm", max_length=32)
    max_context_tokens: int = Field(default=4096, ge=0)
    context_window: int = Field(default=10, ge=0)
    persist_context: bool = True
    context_items: int = 0
    memory: dict | None = None


class AgentMemoryResponse(BaseModel):
    agent_id: str
    memory_type: str
    max_context_tokens: int
    context_window: int
    persist_context: bool
    context_items: int

    model_config = ConfigDict(from_attributes=True)


class AgentMetricEntry(BaseModel):
    id: str
    agent_id: str
    date: datetime
    tasks_completed: int
    tasks_failed: int
    avg_response_time_ms: int
    token_usage: int

    model_config = ConfigDict(from_attributes=True)


class AgentMetricsResponse(BaseModel):
    id: str
    metrics: list[AgentMetricEntry]
    total_tasks_completed: int
    total_tasks_failed: int
    avg_response_time_ms: int
    total_token_usage: int

    model_config = ConfigDict(from_attributes=True)


class DailyMetricEntry(BaseModel):
    date: datetime
    tasks_completed: int
    tasks_failed: int
    avg_response_time_ms: int
    token_usage: int

    model_config = ConfigDict(from_attributes=True)


class AgentDailyMetricsResponse(BaseModel):
    id: str
    start_date: str
    end_date: str
    daily_metrics: list[DailyMetricEntry]

    model_config = ConfigDict(from_attributes=True)


class AgentResetResponse(BaseModel):
    agent_id: str
    status: str
    memory_type: str
    max_context_tokens: int
    context_window: int
    persist_context: bool
    context_items: int
    message: str

    model_config = ConfigDict(from_attributes=True)


class OrgAgentUsageEntry(BaseModel):
    agent_id: str
    agent_name: str
    tasks_completed: int
    tasks_failed: int
    avg_response_time_ms: int
    token_usage: int

    model_config = ConfigDict(from_attributes=True)


class OrgAgentsUsageResponse(BaseModel):
    org_id: str
    total_agents: int
    active_agents: int
    total_tasks_completed: int
    total_tasks_failed: int
    avg_response_time_ms: int
    total_token_usage: int
    agent_usages: list[OrgAgentUsageEntry]

    model_config = ConfigDict(from_attributes=True)


class AgentPerformanceResponse(BaseModel):
    agent_id: str
    status: str
    is_healthy: bool
    tasks_completed: int
    tasks_failed: int
    success_rate: float
    avg_response_time_ms: int
    total_token_usage: int
    uptime_seconds: int
    last_seen_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
