from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.organization import OrganizationMember
from schemas.agent_role import AgentRoleCreate, AgentRoleResponse
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