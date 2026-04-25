import uuid
import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.agent_role import AgentRole
from models.organization import Organization, OrganizationMember
from models.user import User
from schemas.agent_role import AgentRoleCreate, AgentRoleUpdate


class AgentRoleService:
    def __init__(self, db: Session):
        self.db = db

    def create_agent_role(self, data: AgentRoleCreate, user: User) -> AgentRole:
        org_id = data.org_id
        if not org_id:
            # Derive org_id from user's organization membership
            member = self.db.query(OrganizationMember).filter(
                OrganizationMember.user_id == user.id
            ).first()
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": 40001, "message": "User does not belong to any organization"}
                )
            org_id = member.org_id

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

    def update_agent_role(self, agent_role_id: str, data: AgentRoleUpdate, user: User) -> AgentRole | None:
        agent_role = self.get_agent_role_by_id(agent_role_id)
        if not agent_role:
            return None

        if not self.is_org_member(agent_role.org_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "Access denied"}
            )

        # Expire all to ensure fresh state from DB, preventing stale cached objects
        self.db.expire_all()

        if data.name is not None:
            existing = self.db.query(AgentRole).filter(
                AgentRole.name == data.name,
                AgentRole.org_id == agent_role.org_id,
                AgentRole.id != agent_role_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": 40902, "message": "Agent role with this name already exists"}
                )
            agent_role.name = data.name

        if data.description is not None:
            agent_role.description = data.description
        if data.system_prompt_template is not None:
            agent_role.system_prompt_template = data.system_prompt_template
        if data.default_config is not None:
            agent_role.default_config = json.dumps(data.default_config)

        self.db.commit()
        self.db.refresh(agent_role)
        return agent_role

    def delete_agent_role(self, agent_role_id: str, user: User) -> bool:
        agent_role = self.get_agent_role_by_id(agent_role_id)
        if not agent_role:
            return False

        if not self.is_org_member(agent_role.org_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "Access denied"}
            )

        self.db.delete(agent_role)
        self.db.commit()
        return True