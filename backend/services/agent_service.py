import json
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.agent import Agent
from models.organization import Organization, OrganizationMember
from models.project import Project
from models.project_agent import ProjectAgent
from models.user import User
from schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def create_agent(self, data: AgentCreate, user: User) -> Agent:
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

        agent = Agent(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            agent_type=data.agent_type,
            config=json.dumps(data.config) if data.config else None,
            org_id=data.org_id,
            status="offline",
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_org_agents(self, org_id: str) -> list[Agent]:
        return self.db.query(Agent).filter(
            Agent.org_id == org_id,
            Agent.status != "deleted"
        ).all()

    def get_agent_by_id(self, agent_id: str) -> Agent | None:
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def update_agent(self, agent: Agent, data: AgentUpdate) -> Agent:
        if data.name is not None:
            agent.name = data.name
        if data.description is not None:
            agent.description = data.description
        if data.config is not None:
            agent.config = json.dumps(data.config)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete_agent(self, agent: Agent) -> None:
        agent.status = "deleted"
        self.db.commit()

    def is_org_member(self, org_id: str, user: User) -> bool:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user.id
        ).first()
        return member is not None

    def get_agent_status(self, agent: Agent) -> dict:
        return {
            "status": agent.status,
        }

    def assign_agent_to_project(self, agent_id: str, project_id: str) -> ProjectAgent:
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": 40401, "message": "Agent not found"}
            )

        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": 40401, "message": "Project not found"}
            )

        existing = self.db.query(ProjectAgent).filter(
            ProjectAgent.agent_id == agent_id,
            ProjectAgent.project_id == project_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": 40901, "message": "Agent already assigned to this project"}
            )

        project_agent = ProjectAgent(
            id=str(uuid.uuid4()),
            project_id=project_id,
            agent_id=agent_id,
        )
        self.db.add(project_agent)
        self.db.commit()
        self.db.refresh(project_agent)
        return project_agent

    def remove_agent_from_project(self, agent_id: str, project_id: str) -> bool:
        project_agent = self.db.query(ProjectAgent).filter(
            ProjectAgent.agent_id == agent_id,
            ProjectAgent.project_id == project_id
        ).first()
        if not project_agent:
            return False
        self.db.delete(project_agent)
        self.db.commit()
        return True

    def get_project_agents(self, project_id: str) -> list[ProjectAgent]:
        return self.db.query(ProjectAgent).filter(
            ProjectAgent.project_id == project_id
        ).all()

    def get_available_agents_for_project(self, project_id: str, org_id: str) -> list[Agent]:
        project_agent_ids = [pa.agent_id for pa in self.get_project_agents(project_id)]
        return self.db.query(Agent).filter(
            Agent.org_id == org_id,
            Agent.status != "deleted",
            Agent.id.notin_(project_agent_ids) if project_agent_ids else True
        ).all()

    def start_agent(self, agent: Agent) -> dict:
        """Start an agent - sets status to online"""
        agent.status = "online"
        self.db.commit()
        self.db.refresh(agent)
        return {
            "id": agent.id,
            "status": agent.status,
            "message": "Agent started successfully"
        }

    def stop_agent(self, agent: Agent) -> dict:
        """Stop an agent - sets status to offline"""
        agent.status = "offline"
        self.db.commit()
        self.db.refresh(agent)
        return {
            "id": agent.id,
            "status": agent.status,
            "message": "Agent stopped successfully"
        }

    def get_agent_health(self, agent: Agent) -> dict:
        """Get agent health status - returns simulated health data"""
        from datetime import datetime, timezone
        return {
            "id": agent.id,
            "healthy": agent.status in ("online", "busy"),
            "cpu_percent": 45.2 if agent.status == "busy" else 12.5,
            "memory_mb": 256.0 if agent.status == "busy" else 128.0,
            "uptime_seconds": 3600 if agent.status == "online" else 0,
            "last_check_at": datetime.now(timezone.utc)
        }

    def get_agent_logs(self, agent: Agent, limit: int = 100) -> dict:
        """Get agent logs - returns simulated log entries"""
        from datetime import datetime, timezone
        logs = [
            {"timestamp": datetime.now(timezone.utc), "level": "INFO", "message": f"Agent {agent.name} started"},
            {"timestamp": datetime.now(timezone.utc), "level": "INFO", "message": f"Agent {agent.name} initialized"},
        ]
        return {
            "id": agent.id,
            "logs": logs[-limit:],
            "total": len(logs)
        }

    def get_active_agents(self, org_id: str) -> list[Agent]:
        """Get all active agents (online or busy) for an org"""
        return self.db.query(Agent).filter(
            Agent.org_id == org_id,
            Agent.status.in_(["online", "busy"]),
            Agent.status != "deleted"
        ).all()
