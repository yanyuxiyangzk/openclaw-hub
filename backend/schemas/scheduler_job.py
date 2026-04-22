from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class SchedulerJobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    task_template_id: str
    cron_expression: str = Field(..., min_length=1, max_length=64)
    agent_id: str
    enabled: bool = True


class SchedulerJobUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=64)
    agent_id: Optional[str] = None
    enabled: Optional[bool] = None


class SchedulerJobResponse(BaseModel):
    id: str
    name: str
    task_template_id: str
    cron_expression: str
    agent_id: str
    enabled: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SchedulerJobListResponse(BaseModel):
    items: list[SchedulerJobResponse]
    total: int
