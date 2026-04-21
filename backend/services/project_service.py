from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.project import Project
from models.project_member import ProjectMember
from models.organization import Organization, OrganizationMember
from models.user import User
from schemas.project import ProjectCreate, ProjectUpdate
import uuid


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, data: ProjectCreate, user: User) -> Project:
        org = self.db.query(Organization).filter(Organization.id == data.org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": 40401, "message": "Organization not found"}
            )

        if not self.is_org_member(data.org_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "Access denied"}
            )

        project = Project(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            org_id=data.org_id,
            status="active",
            created_by=user.id,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=user.id,
            role="owner",
        )
        self.db.add(member)
        self.db.commit()

        return project

    def get_user_projects(self, user: User) -> list[Project]:
        member_project_ids = [m.project_id for m in user.project_memberships]
        return self.db.query(Project).filter(
            Project.id.in_(member_project_ids),
            Project.status != "deleted"
        ).all()

    def get_project_by_id(self, project_id: str) -> Project | None:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def update_project(self, project: Project, data: ProjectUpdate) -> Project:
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.status is not None:
            project.status = data.status
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project: Project) -> None:
        project.status = "deleted"
        self.db.commit()

    def is_project_member(self, project_id: str, user: User) -> bool:
        member = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        ).first()
        return member is not None

    def get_project_role(self, project_id: str, user_id: str) -> str | None:
        member = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        return member.role if member else None

    def get_project_members(self, project_id: str) -> list[ProjectMember]:
        return self.db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()

    def add_project_member(self, project_id: str, user_id: str, role: str = "member") -> ProjectMember:
        existing = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": 40901, "message": "User is already a project member"}
            )

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_project_member(self, project_id: str, user_id: str) -> bool:
        member = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        if not member:
            return False
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "Cannot remove project owner"}
            )
        self.db.delete(member)
        self.db.commit()
        return True

    def is_org_member(self, org_id: str, user: User) -> bool:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user.id
        ).first()
        return member is not None