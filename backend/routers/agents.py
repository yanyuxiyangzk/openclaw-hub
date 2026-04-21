from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse,
    AgentStatusResponse, AgentProjectAssignRequest, ProjectAgentResponse,
    AgentStartResponse, AgentStopResponse, AgentHealthResponse, AgentLogsResponse, AgentLogEntry
)
from services.agent_service import AgentService
from models.organization import OrganizationMember
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/api/agents", tags=["agents"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_org_id_from_user(db: Session, user: User) -> str | None:
    """Get the first org_id the user belongs to."""
    member = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == user.id
    ).first()
    return member.org_id if member else None


@router.post("", response_model=dict)
def create_agent(data: AgentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents - Create Agent"""
    service = AgentService(db)
    agent = service.create_agent(data, current_user)
    return response(data=AgentResponse.model_validate(agent).model_dump())


@router.get("", response_model=dict)
def list_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents - List Agents"""
    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "User does not belong to any organization"}
        )
    service = AgentService(db)
    agents = service.get_org_agents(org_id)
    return response(data=[AgentResponse.model_validate(a).model_dump() for a in agents])


@router.get("/active", response_model=dict)
def list_active_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/active - List Active Agents (T-234)"""
    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "User does not belong to any organization"}
        )

    service = AgentService(db)
    agents = service.get_active_agents(org_id)
    return response(data=[AgentResponse.model_validate(a).model_dump() for a in agents])


@router.get("/{agent_id}", response_model=dict)
def get_agent(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id} - Get Agent detail"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    return response(data=AgentResponse.model_validate(agent).model_dump())


@router.put("/{agent_id}", response_model=dict)
def update_agent(agent_id: str, data: AgentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/agents/{id} - Update Agent"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    agent = service.update_agent(agent, data)
    return response(data=AgentResponse.model_validate(agent).model_dump())


@router.delete("/{agent_id}", response_model=dict)
def delete_agent(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/agents/{id} - Delete Agent (soft delete)"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    service.delete_agent(agent)
    return response(message="Agent deleted successfully")


@router.get("/{agent_id}/status", response_model=dict)
def get_agent_status(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/status - Get Agent status"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    status_data = service.get_agent_status(agent)
    return response(data=status_data)


@router.post("/{agent_id}/projects/{project_id}", response_model=dict)
def agent_join_project(agent_id: str, project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents/{id}/projects/{project_id} - Agent joins project"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    try:
        project_agent = service.assign_agent_to_project(agent_id, project_id)
    except HTTPException:
        raise
    return response(data=ProjectAgentResponse.model_validate(project_agent).model_dump())


@router.post("/{agent_id}/start", response_model=dict)
def start_agent(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents/{id}/start - Start Agent (T-230)"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if not org_id or agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    result = service.start_agent(agent)
    return response(data=result)


@router.post("/{agent_id}/stop", response_model=dict)
def stop_agent(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents/{id}/stop - Stop Agent (T-231)"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if not org_id or agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    result = service.stop_agent(agent)
    return response(data=result)


@router.get("/{agent_id}/logs", response_model=dict)
def get_agent_logs(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/logs - Get Agent Logs (T-232)"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if not org_id or agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    result = service.get_agent_logs(agent)
    result["logs"] = [AgentLogEntry(**log) for log in result["logs"]]
    return response(data=result)


@router.get("/{agent_id}/health", response_model=dict)
def get_agent_health(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/health - Get Agent Health (T-233)"""
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if not org_id or agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    result = service.get_agent_health(agent)
    return response(data=result)
