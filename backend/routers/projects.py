from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMemberResponse, ProjectMemberListResponse,
    ProjectWithMembersResponse
)
from services.project_service import ProjectService
from services.task_service import TaskService
from models.task import Task

router = APIRouter(prefix="/api/projects", tags=["projects"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


class MemberRoleUpdate(BaseModel):
    role: str


def _task_to_response(task: Task) -> dict:
    import json
    tags = task.tags
    if isinstance(tags, str):
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


@router.post("", response_model=dict)
def create_project(data: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/projects - Create project"""
    service = ProjectService(db)
    project = service.create_project(data, current_user)
    return response(data=ProjectResponse.model_validate(project).model_dump())


@router.get("", response_model=dict)
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/projects - List my projects"""
    service = ProjectService(db)
    projects = service.get_user_projects(current_user)
    return response(data=[ProjectResponse.model_validate(p).model_dump() for p in projects])


@router.get("/{project_id}", response_model=dict)
def get_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/projects/{id} - Project detail"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    members = service.get_project_members(project_id)
    member_items = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        member_items.append(ProjectMemberResponse(
            id=m.id,
            project_id=m.project_id,
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
            user_email=user.email if user else None,
            user_name=user.name if user else None,
        ).model_dump())

    project_data = ProjectResponse.model_validate(project).model_dump()
    project_data["members"] = member_items
    return response(data=project_data)


@router.put("/{project_id}", response_model=dict)
def update_project(project_id: str, data: ProjectUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/projects/{id} - Update project"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.get_project_role(project_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )

    project = service.update_project(project, data)
    return response(data=ProjectResponse.model_validate(project).model_dump())


@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/projects/{id} - Delete project (soft delete)"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.get_project_role(project_id, current_user.id)
    if role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Only owner can delete project"}
        )

    service.delete_project(project)
    return response(message="Project deleted successfully")


@router.get("/{project_id}/members", response_model=dict)
def list_project_members(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/projects/{id}/members - List project members"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    members = service.get_project_members(project_id)
    items = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        items.append(ProjectMemberResponse(
            id=m.id,
            project_id=m.project_id,
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
            user_email=user.email if user else None,
            user_name=user.name if user else None,
        ).model_dump())
    return response(data={"items": items, "total": len(items)})


@router.post("/{project_id}/members", response_model=dict)
def add_project_member(project_id: str, data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/projects/{id}/members - Add project member"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.get_project_role(project_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )

    user_id = data.get("user_id")
    member_role = data.get("role", "member")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 40001, "message": "user_id is required"}
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "User not found"}
        )

    member = service.add_project_member(project_id, user_id, member_role)
    return response(data=ProjectMemberResponse.model_validate(member).model_dump())


@router.delete("/{project_id}/members/{user_id}", response_model=dict)
def remove_project_member(project_id: str, user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/projects/{id}/members/{user_id} - Remove project member"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.get_project_role(project_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )

    try:
        service.remove_project_member(project_id, user_id)
    except HTTPException:
        raise
    return response(message="Member removed successfully")


@router.get("/{project_id}/agents", response_model=dict)
def list_project_agents(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/projects/{id}/agents - List project agents"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    from services.agent_service import AgentService
    agent_service = AgentService(db)
    project_agents = agent_service.get_project_agents(project_id)

    items = []
    for pa in project_agents:
        agent = agent_service.get_agent_by_id(pa.agent_id)
        if agent:
            items.append({
                "id": pa.id,
                "project_id": pa.project_id,
                "agent_id": pa.agent_id,
                "assigned_at": pa.assigned_at,
                "agent_name": agent.name,
                "agent_type": agent.agent_type,
                "agent_status": agent.status,
            })

    return response(data={"items": items, "total": len(items)})


@router.get("/{project_id}/agents/available", response_model=dict)
def list_available_agents(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/projects/{id}/agents/available - List available agents"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    from services.agent_service import AgentService
    from schemas.agent import AgentResponse
    agent_service = AgentService(db)
    available_agents = agent_service.get_available_agents_for_project(project_id, project.org_id)

    return response(data=[AgentResponse.model_validate(a).model_dump() for a in available_agents])


@router.post("/{project_id}/agents", response_model=dict)
def assign_agent_to_project(project_id: str, data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/projects/{id}/agents - Assign Agent to project"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.get_project_role(project_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )

    agent_id = data.get("agent_id")
    if not agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 40001, "message": "agent_id is required"}
        )

    from services.agent_service import AgentService
    from schemas.agent import ProjectAgentResponse
    agent_service = AgentService(db)
    try:
        project_agent = agent_service.assign_agent_to_project(agent_id, project_id)
    except HTTPException:
        raise
    return response(data=ProjectAgentResponse.model_validate(project_agent).model_dump())


@router.delete("/{project_id}/agents/{agent_id}", response_model=dict)
def remove_project_agent(project_id: str, agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/projects/{id}/agents/{agent_id} - Remove Agent from project"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.get_project_role(project_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )

    from services.agent_service import AgentService
    agent_service = AgentService(db)
    success = agent_service.remove_agent_from_project(agent_id, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not assigned to this project"}
        )
    return response(message="Agent removed from project successfully")


@router.get("/{project_id}/tasks", response_model=dict)
def list_project_tasks(
    project_id: str,
    status: str = Query(None),
    assignee_id: str = Query(None),
    priority: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """GET /api/projects/{id}/tasks - List project tasks (T-441)"""
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Project not found"}
        )
    if not service.is_project_member(project_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    task_service = TaskService(db)
    tasks, total = task_service.list_tasks(
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        user=current_user
    )
    return response(data={"items": [_task_to_response(t) for t in tasks], "total": total})