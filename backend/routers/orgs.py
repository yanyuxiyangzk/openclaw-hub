from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationMemberResponse, OrganizationMemberListResponse
)
from schemas.invitation import InvitationCreate, InvitationResponse
from services.org_service import OrgService
from services.agent_service import AgentService

router = APIRouter(prefix="/api/orgs", tags=["organizations"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


@router.post("", response_model=dict)
def create_org(data: OrganizationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/orgs - Create organization"""
    service = OrgService(db)
    org = service.create_org(data, current_user)
    return response(data=OrganizationResponse.model_validate(org).model_dump())


@router.get("", response_model=dict)
def list_my_orgs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/orgs - List my organizations"""
    service = OrgService(db)
    orgs = service.get_user_orgs(current_user)
    return response(data=[OrganizationResponse.model_validate(o).model_dump() for o in orgs])


@router.get("/{org_id}", response_model=dict)
def get_org(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/orgs/{id} - Organization detail"""
    service = OrgService(db)
    org = service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    if not service.is_org_member(org_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )
    return response(data=OrganizationResponse.model_validate(org).model_dump())


@router.put("/{org_id}", response_model=dict)
def update_org(org_id: str, data: OrganizationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/orgs/{id} - Update organization"""
    service = OrgService(db)
    org = service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    if not service.is_org_owner(org, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Only owner can update organization"}
        )
    org = service.update_org(org, data)
    return response(data=OrganizationResponse.model_validate(org).model_dump())


@router.delete("/{org_id}", response_model=dict)
def delete_org(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/orgs/{id} - Delete organization (owner only)"""
    service = OrgService(db)
    org = service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    if not service.is_org_owner(org, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Only owner can delete organization"}
        )
    service.delete_org(org)
    return response(message="Organization deleted successfully")


@router.get("/{org_id}/members", response_model=dict)
def list_org_members(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/orgs/{id}/members - List organization members"""
    service = OrgService(db)
    org = service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    if not service.is_org_member(org_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )
    members = service.get_org_members(org_id)
    items = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        items.append(OrganizationMemberResponse(
            id=m.id,
            org_id=m.org_id,
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
            user_email=user.email if user else None,
            user_name=user.name if user else None,
        ).model_dump())
    return response(data={"items": items, "total": len(items)})


@router.delete("/{org_id}/members/{user_id}", response_model=dict)
def remove_member(org_id: str, user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/orgs/{id}/members/{user_id} - Remove member"""
    service = OrgService(db)
    org = service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    role = service.get_member_role(org_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )
    target_role = service.get_member_role(org_id, user_id)
    if target_role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Cannot remove owner"}
        )
    if not service.remove_member(org_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Member not found"}
        )
    return response(message="Member removed successfully")


@router.post("/{org_id}/invitations", response_model=dict)
def create_invitation(org_id: str, data: InvitationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/orgs/{id}/invitations - Send invitation"""
    service = OrgService(db)
    org = service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    role = service.get_member_role(org_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Admin or owner role required"}
        )
    invitation = service.create_invitation(org_id, data)
    return response(data=InvitationResponse.model_validate(invitation).model_dump())


@router.get("/{org_id}/agents/usage", response_model=dict)
def get_org_agents_usage(org_id: str, days: int = Query(30, ge=1, le=365), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/orgs/{id}/agents/usage - Get agents usage statistics for organization (T-323)"""
    org_service = OrgService(db)
    org = org_service.get_org_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Organization not found"}
        )
    if not org_service.is_org_member(org_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )
    agent_service = AgentService(db)
    usage = agent_service.get_org_agents_usage(org_id, days)
    return response(data=usage)