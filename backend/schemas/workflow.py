from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class WorkflowStep(BaseModel):
    step_id: str
    name: str
    task_template_id: str
    agent_id: str
    depends_on: list[str] = []
    config: Optional[dict] = None


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    steps: list[WorkflowStep]


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None
    steps: Optional[list[WorkflowStep]] = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    steps: list[dict]
    org_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecuteRequest(BaseModel):
    input_data: Optional[dict] = None
    agent_id: Optional[str] = None
