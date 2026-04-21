from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


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
