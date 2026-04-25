from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = None
    project_id: Optional[str] = None  # Required for direct task creation, inherited from parent for subtasks
    status: str = "todo"
    priority: str = "medium"
    parent_id: Optional[str] = None
    root_id: Optional[str] = None
    position: int = 0
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tags: Optional[list[str]] = []
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    assignee_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    parent_id: Optional[str] = None
    root_id: Optional[str] = None
    position: Optional[int] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    assignee_id: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    parent_id: Optional[str]
    root_id: Optional[str]
    position: int
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    tags: Optional[list[str]]
    due_date: Optional[datetime]
    reminder_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    project_id: str
    assignee_id: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int


class TaskBulkCreate(BaseModel):
    tasks: list[TaskCreate]


class TaskBulkStatusUpdate(BaseModel):
    task_ids: list[str]
    status: str


class TaskMoveRequest(BaseModel):
    status: Optional[str] = None
    position: Optional[int] = None
    assignee_id: Optional[str] = None


class TaskAssignRequest(BaseModel):
    assignee_id: str


class TaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class TaskCommentResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    author_email: Optional[str] = None
    author_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCommentListResponse(BaseModel):
    items: list[TaskCommentResponse]
    total: int


class TaskAttachmentResponse(BaseModel):
    id: str
    task_id: str
    filename: str
    file_url: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime
    uploader_email: Optional[str] = None
    uploader_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskAttachmentListResponse(BaseModel):
    items: list[TaskAttachmentResponse]
    total: int


class KanbanColumnResponse(BaseModel):
    status: str
    tasks: list[TaskResponse]
    count: int


class KanbanBoardResponse(BaseModel):
    columns: list[KanbanColumnResponse]
    total: int


class TaskActivityResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    action: str
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None


class TaskFilterRequest(BaseModel):
    project_id: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None


class ReminderRequest(BaseModel):
    reminder_at: datetime


class SnoozeRequest(BaseModel):
    snooze_minutes: int = Field(..., ge=1, le=10080)


class DueSoonTaskResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    overdue: int
    due_today: int
    due_this_week: int
