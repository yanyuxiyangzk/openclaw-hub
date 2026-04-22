import uuid
import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.agent_role import AgentRole
from models.organization import Organization, OrganizationMember
from models.user import User
from schemas.agent_role import AgentRoleCreate


class AgentRoleService:
    def __init__(self, db: Session):
        self.db = db

    def create_agent_role(self, data: AgentRoleCreate, user: User) -> AgentRole:
        org_id = data.org_id
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": 40001, "message": "org_id is required"}
            )

        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": 40401, "message": "Organization not found"}
            )

        if not self.is_org_member(org_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "Access denied"}
            )

        existing = self.db.query(AgentRole).filter(
            AgentRole.name == data.name,
            AgentRole.org_id == org_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": 40902, "message": "Agent role with this name already exists"}
            )

        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            system_prompt_template=data.system_prompt_template,
            default_config=json.dumps(data.default_config) if data.default_config else None,
            org_id=org_id,
        )
        self.db.add(agent_role)
        self.db.commit()
        self.db.refresh(agent_role)
        return agent_role

    def get_org_agent_roles(self, org_id: str) -> list[AgentRole]:
        return self.db.query(AgentRole).filter(AgentRole.org_id == org_id).all()

    def get_agent_role_by_id(self, agent_role_id: str) -> AgentRole | None:
        return self.db.query(AgentRole).filter(AgentRole.id == agent_role_id).first()

    def is_org_member(self, org_id: str, user: User) -> bool:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user.id
        ).first()
        return member is not None