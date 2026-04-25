from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.organization import OrganizationMember
from schemas.agent_role import AgentRoleCreate, AgentRoleUpdate, AgentRoleResponse
from services.agent_role_service import AgentRoleService

router = APIRouter(prefix="/api/agent-roles", tags=["agent-roles"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_org_id_from_user(db: Session, user: User) -> str | None:
    """Get the first org_id the user belongs to."""
    member = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == user.id
    ).first()
    return member.org_id if member else None


@router.post("", response_model=dict)
def create_agent_role(data: AgentRoleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agent-roles - Create Agent Role"""
    service = AgentRoleService(db)
    agent_role = service.create_agent_role(data, current_user)
    return response(data=AgentRoleResponse.model_validate(agent_role).model_dump())


@router.get("", response_model=dict)
def list_agent_roles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agent-roles - List Agent Roles for user's org"""
    service = AgentRoleService(db)
    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 40001, "message": "User does not belong to any organization"}
        )
    agent_roles = service.get_org_agent_roles(org_id)
    return response(data=[AgentRoleResponse.model_validate(ar).model_dump() for ar in agent_roles])


@router.get("/{agent_role_id}", response_model=dict)
def get_agent_role(agent_role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agent-roles/{id} - Get Agent Role by ID"""
    service = AgentRoleService(db)
    agent_role = service.get_agent_role_by_id(agent_role_id)
    if not agent_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent role not found"}
        )

    if not service.is_org_member(agent_role.org_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    return response(data=AgentRoleResponse.model_validate(agent_role).model_dump())

@router.put("/{agent_role_id}", response_model=dict)
def update_agent_role(agent_role_id: str, data: AgentRoleUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/agent-roles/{id} - Update Agent Role"""
    service = AgentRoleService(db)
    agent_role = service.update_agent_role(agent_role_id, data, current_user)
    if not agent_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent role not found"}
        )
    return response(data=AgentRoleResponse.model_validate(agent_role).model_dump())


@router.delete("/{agent_role_id}", response_model=dict)
def delete_agent_role(agent_role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/agent-roles/{id} - Delete Agent Role"""
    service = AgentRoleService(db)
    deleted = service.delete_agent_role(agent_role_id, current_user)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent role not found"}
        )
    return response(code=0, message="Agent role deleted successfully")
