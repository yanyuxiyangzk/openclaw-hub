import json
from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime, date


class AgentRoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    system_prompt_template: str | None = None
    default_config: dict | None = None
    org_id: str | None = None  # Optional - backend derives from JWT if not provided


class AgentRoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    description: str | None = None
    system_prompt_template: str | None = None
    default_config: dict | None = None


class AgentRoleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    system_prompt_template: str | None
    default_config: dict | None
    org_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def deserialize_default_config(cls, data):
        if hasattr(data, "default_config") and isinstance(data.default_config, str):
            data.default_config = json.loads(data.default_config) if data.default_config else None
        return data


class AgentSkillBindRequest(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=128)
    skill_config: dict | None = None
    enabled: bool = True


class AgentSkillUpdate(BaseModel):
    skill_config: dict | None = None
    enabled: bool | None = None


class AgentSkillResponse(BaseModel):
    id: str
    agent_id: str
    skill_name: str
    skill_config: dict | None
    enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def deserialize_skill_config(cls, data):
        if hasattr(data, "skill_config") and isinstance(data.skill_config, str):
            data.skill_config = json.loads(data.skill_config) if data.skill_config else None
        return data


class AgentMemoryConfig(BaseModel):
    memory_type: str = Field(default="shortterm", max_length=32)
    max_context_tokens: int = Field(default=4096, ge=0)
    context_window: int = Field(default=10, ge=0)
    persist_context: bool = True


class AgentMemoryResponse(BaseModel):
    agent_id: str
    memory_type: str
    max_context_tokens: int
    context_window: int
    persist_context: bool
    context_items: int

    model_config = ConfigDict(from_attributes=True)


class AgentContextRequest(BaseModel):
    context: dict


class AgentHistoryResponse(BaseModel):
    agent_id: str
    messages: list[dict]
    total: int

    model_config = ConfigDict(from_attributes=True)


class AgentMetricsResponse(BaseModel):
    id: str
    agent_id: str
    date: date
    tasks_completed: int
    tasks_failed: int
    avg_response_time_ms: int
    token_usage: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentDailyStatsResponse(BaseModel):
    agent_id: str
    date: date
    tasks_completed: int
    tasks_failed: int
    avg_response_time_ms: int
    token_usage: int

    model_config = ConfigDict(from_attributes=True)


class AgentTaskCountResponse(BaseModel):
    agent_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int

    model_config = ConfigDict(from_attributes=True)


class OrgAgentUsageResponse(BaseModel):
    org_id: str
    total_agents: int
    active_agents: int
    total_tasks_completed: int
    total_token_usage: int
    agents: list[dict]

    model_config = ConfigDict(from_attributes=True)


class AgentPerformanceResponse(BaseModel):
    agent_id: str
    period_start: str
    period_end: str
    total_tasks: int
    success_rate: float
    avg_response_time_ms: int
    avg_tokens_per_task: int
    uptime_percent: float

    model_config = ConfigDict(from_attributes=True)


class AgentHealthDetailResponse(BaseModel):
    id: str
    healthy: bool
    status: str
    cpu_percent: float | None
    memory_mb: float | None
    uptime_seconds: int | None
    last_check_at: datetime
    error_count_today: int

    model_config = ConfigDict(from_attributes=True)