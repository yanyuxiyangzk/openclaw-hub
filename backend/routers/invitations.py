from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.invitation import InvitationResponse, InvitationValidateResponse, InvitationAcceptResponse
from services.org_service import OrgService

router = APIRouter(prefix="/api/invitations", tags=["invitations"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


@router.get("/{token}", response_model=dict)
def validate_invitation(token: str, db: Session = Depends(get_db)):
    """GET /api/invitations/{token} - Validate invitation"""
    service = OrgService(db)
    invitation = service.get_invitation_by_token(token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Invitation not found"}
        )
    org = service.get_org_by_id(invitation.org_id)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    expires_at = invitation.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    is_valid = (
        invitation.status == "pending" and
        expires_at > now
    )
    return response(data={
        "valid": is_valid,
        "invitation": InvitationResponse.model_validate(invitation).model_dump() if is_valid else None,
        "organization_name": org.name if org else None,
    })


@router.post("/{token}/accept", response_model=dict)
def accept_invitation(token: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/invitations/{token}/accept - Accept invitation"""
    service = OrgService(db)
    invitation = service.get_invitation_by_token(token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Invitation not found"}
        )
    org = service.get_org_by_id(invitation.org_id)
    try:
        member = service.accept_invitation(invitation, current_user)
    except HTTPException:
        raise
    return response(data={
        "success": True,
        "message": "Invitation accepted successfully",
        "organization_id": org.id if org else None,
        "organization_name": org.name if org else None,
    })


@router.delete("/{invitation_id}", response_model=dict)
def revoke_invitation(invitation_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/invitations/{id} - Revoke invitation"""
    service = OrgService(db)
    invitation = service.get_invitation_by_id(invitation_id)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Invitation not found"}
        )
    try:
        service.revoke_invitation(invitation_id, current_user)
    except HTTPException:
        raise
    return response(message="Invitation revoked successfully")