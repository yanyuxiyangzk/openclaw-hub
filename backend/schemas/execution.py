from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class ExecutionCreate(BaseModel):
    task_id: str
    agent_id: str
    input_data: Optional[dict] = None


class ExecutionResponse(BaseModel):
    id: str
    task_id: str
    agent_id: str
    status: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionListResponse(BaseModel):
    items: list[ExecutionResponse]
    total: int


class ExecutionOutputResponse(BaseModel):
    id: str
    output_data: Optional[dict] = None
    status: str
