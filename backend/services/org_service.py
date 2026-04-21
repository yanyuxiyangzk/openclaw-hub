from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.organization import Organization, OrganizationMember
from models.invitation import Invitation
from models.user import User
from schemas.organization import OrganizationCreate, OrganizationUpdate
from schemas.invitation import InvitationCreate
from datetime import datetime, timedelta, timezone
import secrets


class OrgService:
    def __init__(self, db: Session):
        self.db = db

    def create_org(self, data: OrganizationCreate, owner: User) -> Organization:
        org = Organization(
            name=data.name,
            owner_id=owner.id,
        )
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)

        member = OrganizationMember(
            org_id=org.id,
            user_id=owner.id,
            role="owner",
        )
        self.db.add(member)
        self.db.commit()
        return org

    def get_user_orgs(self, user: User) -> list[Organization]:
        member_ids = [m.org_id for m in user.memberships]
        return self.db.query(Organization).filter(Organization.id.in_(member_ids)).all()

    def get_org_by_id(self, org_id: str) -> Organization | None:
        return self.db.query(Organization).filter(Organization.id == org_id).first()

    def update_org(self, org: Organization, data: OrganizationUpdate) -> Organization:
        org.name = data.name
        self.db.commit()
        self.db.refresh(org)
        return org

    def delete_org(self, org: Organization) -> None:
        self.db.delete(org)
        self.db.commit()

    def get_org_members(self, org_id: str) -> list[OrganizationMember]:
        return self.db.query(OrganizationMember).filter(OrganizationMember.org_id == org_id).all()

    def remove_member(self, org_id: str, user_id: str) -> bool:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user_id
        ).first()
        if not member:
            return False
        self.db.delete(member)
        self.db.commit()
        return True

    def is_org_owner(self, org: Organization, user: User) -> bool:
        return org.owner_id == user.id

    def is_org_member(self, org_id: str, user: User) -> bool:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user.id
        ).first()
        return member is not None

    def get_member_role(self, org_id: str, user_id: str) -> str | None:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user_id
        ).first()
        return member.role if member else None

    def create_invitation(self, org_id: str, data: InvitationCreate) -> Invitation:
        invitation = Invitation(
            org_id=org_id,
            email=data.email,
            role=data.role,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            status="pending",
        )
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)
        return invitation

    def get_invitation_by_token(self, token: str) -> Invitation | None:
        return self.db.query(Invitation).filter(Invitation.token == token).first()

    def get_invitation_by_id(self, invitation_id: str) -> Invitation | None:
        return self.db.query(Invitation).filter(Invitation.id == invitation_id).first()

    def accept_invitation(self, invitation: Invitation, user: User) -> OrganizationMember:
        if invitation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": 42201, "message": "Invitation is not pending"}
            )
        now = datetime.now(timezone.utc)
        expires_at = invitation.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            invitation.status = "expired"
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": 42201, "message": "Invitation has expired"}
            )

        existing = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == invitation.org_id,
            OrganizationMember.user_id == user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": 40901, "message": "Already a member"}
            )

        invitation.status = "accepted"
        member = OrganizationMember(
            org_id=invitation.org_id,
            user_id=user.id,
            role=invitation.role,
        )
        self.db.add(member)
        self.db.commit()
        return member

    def revoke_invitation(self, invitation_id: str, user: User) -> bool:
        invitation = self.get_invitation_by_id(invitation_id)
        if not invitation:
            return False
        org = self.get_org_by_id(invitation.org_id)
        if not org or not self.is_org_owner(org, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "Only owner can revoke invitations"}
            )
        self.db.delete(invitation)
        self.db.commit()
        return True

    def get_org_invitations(self, org_id: str) -> list[Invitation]:
        return self.db.query(Invitation).filter(Invitation.org_id == org_id).all()