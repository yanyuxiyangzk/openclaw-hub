from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.task import Task
from models.task_comment import TaskComment
from models.task_attachment import TaskAttachment
from schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskBulkCreate, TaskBulkStatusUpdate, TaskMoveRequest,
    TaskAssignRequest, TaskCommentCreate, TaskCommentResponse,
    TaskCommentListResponse, TaskAttachmentResponse, TaskAttachmentListResponse,
    KanbanColumnResponse, KanbanBoardResponse, TaskActivityResponse,
    ReminderRequest, SnoozeRequest, DueSoonTaskResponse
)
from services.task_service import TaskService
from datetime import datetime

router = APIRouter(prefix="/api", tags=["tasks"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


def _task_to_response(task: Task) -> dict:
    tags = task.tags
    if isinstance(tags, str):
        import json
        try:
            tags = json.loads(tags)
        except:
            tags = None

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "parent_id": task.parent_id,
        "root_id": task.root_id,
        "position": task.position,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "tags": tags,
        "due_date": task.due_date,
        "reminder_at": task.reminder_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "project_id": task.project_id,
        "assignee_id": task.assignee_id,
        "created_by": task.created_by,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "comment_count": len(task.comments) if task.comments else 0,
        "subtask_count": len(task.subtasks) if task.subtasks else 0
    }


def _comment_to_response(comment: TaskComment) -> dict:
    return {
        "id": comment.id,
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "author_email": comment.author.email if comment.author else None,
        "author_name": comment.author.name if comment.author else None
    }


def _attachment_to_response(attachment: TaskAttachment) -> dict:
    return {
        "id": attachment.id,
        "task_id": attachment.task_id,
        "filename": attachment.filename,
        "file_url": attachment.file_url,
        "file_size": attachment.file_size,
        "uploaded_by": attachment.uploaded_by,
        "uploaded_at": attachment.uploaded_at,
        "uploader_email": attachment.uploader.email if attachment.uploader else None,
        "uploader_name": attachment.uploader.name if attachment.uploader else None
    }


# ========== Task CRUD (T-401 ~ T-408) ==========

@router.post("/tasks", response_model=dict)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks - Create task (T-401)"""
    try:
        task = service.create_task(data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/tasks", response_model=dict)
def list_tasks(
    project_id: str = Query(None),
    status: str = Query(None),
    assignee_id: str = Query(None),
    priority: str = Query(None),
    due: str = Query(None),  # overdue | today | this_week | no_date
    tags: str = Query(None),  # comma-separated tags
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks - List tasks (T-402)"""
    # Parse tags if provided
    tag_list = tags.split(",") if tags else None
    tasks, total = service.list_tasks(
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        due=due,
        tags=tag_list,
        user=current_user
    )
    return response(data={"items": [_task_to_response(t) for t in tasks], "total": total})


@router.get("/tasks/due-soon", response_model=dict)
def get_due_soon_tasks(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/due-soon - Tasks due soon (T-431)"""
    result = service.get_due_soon_tasks(current_user, hours)
    return response(data={
        "tasks": [_task_to_response(t) for t in result["tasks"]],
        "total": result["total"],
        "overdue": result["overdue"],
        "due_today": result["due_today"],
        "due_this_week": result["due_this_week"]
    })


@router.get("/tasks/export", response_model=dict)
def export_tasks(
    project_id: str = Query(...),
    format: str = Query("json"),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/export - Export tasks (T-408)"""
    try:
        result = service.export_tasks(project_id, format, current_user)
        return response(data={"format": format, "content": result})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})


@router.get("/tasks/{task_id}", response_model=dict)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/{id} - Get task (T-403)"""
    try:
        task = service.get_task(task_id, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.put("/tasks/{task_id}", response_model=dict)
def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """PUT /api/tasks/{id} - Update task (T-404)"""
    try:
        task = service.update_task(task_id, data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.delete("/tasks/{task_id}", response_model=dict)
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """DELETE /api/tasks/{id} - Delete task (T-405)"""
    try:
        service.delete_task(task_id, current_user)
        return response(message="Task deleted successfully")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/bulk", response_model=dict)
def bulk_create_tasks(
    data: TaskBulkCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/bulk - Bulk create (T-406)"""
    try:
        tasks = service.bulk_create_tasks(data, current_user)
        return response(data={"items": [_task_to_response(t) for t in tasks], "total": len(tasks)})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.put("/tasks/bulk/status", response_model=dict)
def bulk_update_status(
    data: TaskBulkStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """PUT /api/tasks/bulk/status - Bulk status update (T-407)"""
    try:
        tasks = service.bulk_update_status(data, current_user)
        return response(data={"items": [_task_to_response(t) for t in tasks], "total": len(tasks)})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


# ========== Task Collaboration (T-410 ~ T-417) ==========

@router.post("/tasks/{task_id}/assign", response_model=dict)
def assign_task(
    task_id: str,
    data: TaskAssignRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/assign - Assign task (T-410)"""
    try:
        task = service.assign_task(task_id, data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/claim", response_model=dict)
def claim_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/claim - Claim task (T-411)"""
    try:
        task = service.claim_task(task_id, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/complete", response_model=dict)
def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/complete - Complete task (T-412)"""
    try:
        task = service.complete_task(task_id, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/comment", response_model=dict)
def add_comment(
    task_id: str,
    data: TaskCommentCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/comment - Add comment (T-413)"""
    try:
        comment = service.add_comment(task_id, data, current_user)
        return response(data=_comment_to_response(comment))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/tasks/{task_id}/comments", response_model=dict)
def get_comments(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/{id}/comments - List comments (T-414)"""
    try:
        comments, total = service.get_comments(task_id, current_user)
        return response(data={"items": [_comment_to_response(c) for c in comments], "total": total})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/subtasks", response_model=dict)
def create_subtask(
    task_id: str,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/subtasks - Create subtask (T-415)"""
    try:
        task = service.create_subtask(task_id, data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/tasks/{task_id}/subtasks", response_model=dict)
def get_subtasks(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/{id}/subtasks - List subtasks (T-416)"""
    try:
        subtasks, total = service.get_subtasks(task_id, current_user)
        return response(data={"items": [_task_to_response(t) for t in subtasks], "total": total})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/attachments", response_model=dict)
async def upload_attachment(
    task_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/attachments - Upload attachment (T-417)"""
    try:
        import os
        import uuid
        from config import get_settings
        settings = get_settings()

        upload_dir = os.path.join("uploads", "tasks", task_id)
        os.makedirs(upload_dir, exist_ok=True)

        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_url = f"/uploads/tasks/{task_id}/{unique_filename}"
        file_size = len(content)

        attachment = service.add_attachment(
            task_id, file.filename, file_url, file_size, current_user
        )
        return response(data=_attachment_to_response(attachment))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/tasks/{task_id}/attachments", response_model=dict)
def get_attachments(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/{id}/attachments - List attachments (T-417a)"""
    try:
        attachments, total = service.get_attachments(task_id, current_user)
        return response(data={"items": [_attachment_to_response(a) for a in attachments], "total": total})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


# ========== Kanban Views (T-420 ~ T-425) ==========

@router.get("/projects/{project_id}/kanban", response_model=dict)
def get_kanban_board(
    project_id: str,
    priority: str = Query(None),
    assignee_id: str = Query(None),
    due: str = Query(None),  # overdue | today | this_week | no_date
    tags: str = Query(None),  # comma-separated tags
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/projects/{id}/kanban - Kanban data (T-420)"""
    try:
        tag_list = tags.split(",") if tags else None
        result = service.get_kanban_board(project_id, current_user, priority=priority, assignee_id=assignee_id, due=due, tags=tag_list)
        return response(data={
            "columns": [
                {
                    "status": col["status"],
                    "tasks": [_task_to_response(t) for t in col["tasks"]],
                    "count": col["count"]
                }
                for col in result["columns"]
            ],
            "total": result["total"]
        })
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/projects/{project_id}/tasks/by-status", response_model=dict)
def get_tasks_by_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/projects/{id}/tasks/by-status - By status (T-421)"""
    try:
        result = service.get_tasks_by_status(project_id, current_user)
        return response(data={k: [_task_to_response(t) for t in v] for k, v in result.items()})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/projects/{project_id}/tasks/by-assignee", response_model=dict)
def get_tasks_by_assignee(
    project_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/projects/{id}/tasks/by-assignee - By assignee (T-422)"""
    try:
        result = service.get_tasks_by_assignee(project_id, current_user)
        return response(data={k: [_task_to_response(t) for t in v] for k, v in result.items()})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/projects/{project_id}/tasks/timeline", response_model=dict)
def get_timeline(
    project_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/projects/{id}/tasks/timeline - Timeline view (T-423)"""
    try:
        tasks = service.get_timeline(project_id, current_user)
        return response(data=[_task_to_response(t) for t in tasks])
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/move", response_model=dict)
def move_task(
    task_id: str,
    data: TaskMoveRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/move - Move task (T-424)"""
    try:
        task = service.move_task(task_id, data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/tasks/{task_id}/activity", response_model=dict)
def get_activity(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """GET /api/tasks/{id}/activity - Activity history (T-425)"""
    try:
        activities = service.get_activity(task_id, current_user)
        return response(data=activities)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


# ========== Reminders (T-430 ~ T-432) ==========

@router.post("/tasks/{task_id}/remind", response_model=dict)
def set_reminder(
    task_id: str,
    data: ReminderRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/remind - Set reminder (T-430)"""
    try:
        task = service.set_reminder(task_id, data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/snooze", response_model=dict)
def snooze_reminder(
    task_id: str,
    data: SnoozeRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """POST /api/tasks/{id}/snooze - Snooze reminder (T-432)"""
    try:
        task = service.snooze_reminder(task_id, data, current_user)
        return response(data=_task_to_response(task))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})
