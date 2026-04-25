import json
import uuid
from datetime import date
from sqlalchemy.orm import Session
from models.agent import Agent
from models.agent_skill import AgentSkill
from models.agent_metric import AgentMetric
from models.organization import Organization, OrganizationMember
from models.project import Project
from models.project_agent import ProjectAgent
from models.user import User
from schemas.agent import AgentCreate, AgentUpdate
from schemas.agent_role import AgentSkillBindRequest
from core.exceptions import (
    NotFoundException, ForbiddenException, ConflictException,
    OrganizationNotFoundException, AgentNotFoundException,
    ProjectNotFoundException, AgentAlreadyAssignedException,
    AgentNotAssignedException
)


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def create_agent(self, data: AgentCreate, user: User) -> Agent:
        org = self.db.query(Organization).filter(Organization.id == data.org_id).first()
        if not org:
            raise OrganizationNotFoundException(data.org_id)

        if not self.is_org_member(data.org_id, user):
            raise ForbiddenException(message="Access denied")

        agent_config = json.dumps(data.config) if data.config else None
        agent = Agent(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            agent_type=data.agent_type,
            config=agent_config,
            org_id=data.org_id,
            status="offline",
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        # Parse config back to dict for response consistency
        if agent.config:
            agent.config = json.loads(agent.config)
        return agent

    def get_org_agents(self, org_id: str) -> list[Agent]:
        return self.db.query(Agent).filter(
            Agent.org_id == org_id,
            Agent.status != "deleted"
        ).all()

    def get_agent_by_id(self, agent_id: str) -> Agent | None:
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if agent and agent.config:
            agent.config = json.loads(agent.config)
        return agent

    def get_agent_by_id_for_memory_op(self, agent_id: str) -> Agent | None:
        """Get agent without modifying config to avoid dirty-tracking issues."""
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
        if agent.config:
            agent.config = json.loads(agent.config)
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
            raise AgentNotFoundException(agent_id)

        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ProjectNotFoundException(project_id)

        existing = self.db.query(ProjectAgent).filter(
            ProjectAgent.agent_id == agent_id,
            ProjectAgent.project_id == project_id
        ).first()
        if existing:
            raise AgentAlreadyAssignedException()

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
        """Get agent health status - returns health data with error_count_today"""
        from datetime import datetime, timezone, timedelta
        from sqlalchemy import func

        today = date.today()
        error_count = self.db.query(func.sum(AgentMetric.tasks_failed)).filter(
            AgentMetric.agent_id == agent.id,
            AgentMetric.date >= today - timedelta(days=1)
        ).scalar() or 0

        return {
            "id": agent.id,
            "healthy": agent.status in ("online", "busy"),
            "status": agent.status,
            "cpu_percent": 45.2 if agent.status == "busy" else 12.5,
            "memory_mb": 256.0 if agent.status == "busy" else 128.0,
            "uptime_seconds": 3600 if agent.status == "online" else 0,
            "last_check_at": datetime.now(timezone.utc).isoformat(),
            "error_count_today": error_count,
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
            Agent.status.in_(["online", "busy"])
        ).all()

    def bind_skill(self, agent_id: str, data: AgentSkillBindRequest) -> AgentSkill:
        """Bind a skill to an agent"""
        agent = self.get_agent_by_id(agent_id)
        if not agent:
            raise AgentNotFoundException(agent_id)

        existing = self.db.query(AgentSkill).filter(
            AgentSkill.agent_id == agent_id,
            AgentSkill.skill_name == data.skill_name
        ).first()
        if existing:
            raise ConflictException(message="Skill already bound to this agent")

        skill = AgentSkill(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            skill_name=data.skill_name,
            skill_config=json.dumps(data.skill_config) if data.skill_config else None,
            enabled=data.enabled,
        )
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        if skill.skill_config:
            skill.skill_config = json.loads(skill.skill_config)
        return skill

    def get_agent_skills(self, agent_id: str) -> list[AgentSkill]:
        """Get all skills bound to an agent"""
        return self.db.query(AgentSkill).filter(AgentSkill.agent_id == agent_id).all()

    def unbind_skill(self, agent_id: str, skill_id: str) -> bool:
        """Unbind (delete) a skill from an agent"""
        skill = self.db.query(AgentSkill).filter(
            AgentSkill.id == skill_id,
            AgentSkill.agent_id == agent_id
        ).first()
        if not skill:
            return False
        self.db.delete(skill)
        self.db.commit()
        return True

    def get_agent_history(self, agent: Agent, page: int = 1, limit: int = 20) -> dict:
        """Get agent activity history"""
        from models.activity import Activity
        from schemas.activity import ActivityResponse
        from sqlalchemy import desc

        query = self.db.query(Activity).filter(
            Activity.entity_type == "agent",
            Activity.entity_id == agent.id
        )

        total = query.count()
        items = query.order_by(desc(Activity.created_at)).offset((page - 1) * limit).limit(limit).all()
        pages = (total + limit - 1) // limit if total > 0 else 1

        return {
            "items": [ActivityResponse.model_validate(a).model_dump() for a in items],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    def get_agent_config(self, agent: Agent) -> dict:
        """Get agent configuration"""
        config = agent.config if isinstance(agent.config, dict) else (json.loads(agent.config) if agent.config else None)
        return {
            "id": agent.id,
            "config": config
        }

    def update_agent_config(self, agent: Agent, config: dict | None) -> dict:
        """Update agent configuration"""
        agent.config = json.dumps(config) if config is not None else None
        self.db.commit()
        self.db.refresh(agent)
        if agent.config:
            agent.config = json.loads(agent.config)
        return {
            "id": agent.id,
            "config": agent.config
        }

    def get_agent_memory(self, agent: Agent) -> dict:
        """Get agent memory config and content"""
        config = agent.config if isinstance(agent.config, dict) else (json.loads(agent.config) if agent.config else {})
        memory_content = json.loads(agent.memory) if agent.memory else None
        context_items = 0
        if memory_content and isinstance(memory_content, dict):
            context_items = len(memory_content.get("context", [])) if "context" in memory_content else 0
        return {
            "agent_id": agent.id,
            "memory_type": config.get("memory_type", "shortterm"),
            "max_context_tokens": config.get("max_context_tokens", 4096),
            "context_window": config.get("context_window", 10),
            "persist_context": config.get("persist_context", True),
            "context_items": context_items,
        }

    def update_agent_memory(self, agent: Agent, memory_data: dict) -> dict:
        """Update agent memory config and content"""
        config = agent.config if isinstance(agent.config, dict) else (json.loads(agent.config) if agent.config else {})
        config["memory_type"] = memory_data.get("memory_type", "shortterm")
        config["max_context_tokens"] = memory_data.get("max_context_tokens", 4096)
        config["context_window"] = memory_data.get("context_window", 10)
        config["persist_context"] = memory_data.get("persist_context", True)
        agent.config = json.dumps(config)

        if memory_data.get("memory") is not None:
            agent.memory = json.dumps(memory_data["memory"])
        self.db.commit()
        self.db.refresh(agent)

        memory_content = json.loads(agent.memory) if agent.memory else None
        context_items = 0
        if memory_content and isinstance(memory_content, dict):
            context_items = len(memory_content.get("context", [])) if "context" in memory_content else 0
        return {
            "agent_id": agent.id,
            "memory_type": config["memory_type"],
            "max_context_tokens": config["max_context_tokens"],
            "context_window": config["context_window"],
            "persist_context": config["persist_context"],
            "context_items": context_items,
        }

    def clear_agent_memory(self, agent: Agent) -> dict:
        """Clear agent memory content but keep config"""
        agent.memory = None
        self.db.commit()
        self.db.refresh(agent)
        config = agent.config if isinstance(agent.config, dict) else (json.loads(agent.config) if agent.config else {})
        return {
            "agent_id": agent.id,
            "memory_type": config.get("memory_type", "shortterm"),
            "max_context_tokens": config.get("max_context_tokens", 4096),
            "context_window": config.get("context_window", 10),
            "persist_context": config.get("persist_context", True),
            "context_items": 0,
        }

    def reset_agent(self, agent: Agent) -> dict:
        """Reset an agent - stops it and clears memory"""
        agent.status = "offline"
        agent.memory = None
        self.db.commit()
        self.db.refresh(agent)
        config = agent.config if isinstance(agent.config, dict) else (json.loads(agent.config) if agent.config else {})
        return {
            "agent_id": agent.id,
            "status": agent.status,
            "memory_type": config.get("memory_type", "shortterm"),
            "max_context_tokens": config.get("max_context_tokens", 4096),
            "context_window": config.get("context_window", 10),
            "persist_context": config.get("persist_context", True),
            "context_items": 0,
            "message": "Agent reset successfully"
        }

    def get_agent_metrics(self, agent: Agent, days: int = 30) -> dict:
        """Get agent metrics for the specified number of days"""
        from datetime import datetime, timezone, timedelta
        from schemas.agent import AgentMetricsResponse, AgentMetricEntry

        start_date = datetime.now(timezone.utc).date() - timedelta(days=days)

        metrics = self.db.query(AgentMetric).filter(
            AgentMetric.agent_id == agent.id,
            AgentMetric.date >= start_date
        ).order_by(AgentMetric.date.desc()).all()

        metric_entries = []
        total_tasks_completed = 0
        total_tasks_failed = 0
        total_token_usage = 0

        for m in metrics:
            entry = AgentMetricEntry(
                id=m.id,
                agent_id=m.agent_id,
                date=m.date,
                tasks_completed=m.tasks_completed,
                tasks_failed=m.tasks_failed,
                avg_response_time_ms=m.avg_response_time_ms,
                token_usage=m.token_usage,
            )
            metric_entries.append(entry)
            total_tasks_completed += m.tasks_completed
            total_tasks_failed += m.tasks_failed
            total_token_usage += m.token_usage

        avg_response_time_ms = 0
        if metrics:
            avg_response_time_ms = int(sum(m.avg_response_time_ms for m in metrics) / len(metrics))

        return AgentMetricsResponse(
            id=agent.id,
            metrics=metric_entries,
            total_tasks_completed=total_tasks_completed,
            total_tasks_failed=total_tasks_failed,
            avg_response_time_ms=avg_response_time_ms,
            total_token_usage=total_token_usage,
        ).model_dump()

    def get_agent_daily_metrics(self, agent: Agent, start_date: date, end_date: date) -> list[dict]:
        """Get agent daily metrics for a specific date range (T-321)"""
        metrics = self.db.query(AgentMetric).filter(
            AgentMetric.agent_id == agent.id,
            AgentMetric.date >= start_date,
            AgentMetric.date <= end_date
        ).order_by(AgentMetric.date.asc()).all()

        return [
            {
                "agent_id": agent.id,
                "date": m.date.isoformat() if isinstance(m.date, date) else m.date,
                "tasks_completed": m.tasks_completed,
                "tasks_failed": m.tasks_failed,
                "avg_response_time_ms": m.avg_response_time_ms,
                "token_usage": m.token_usage,
            }
            for m in metrics
        ]

    def get_agent_task_counts(self, agent: Agent) -> dict:
        """Get task execution counts for an agent (T-322)"""
        from models.execution import Execution, ExecutionStatus

        total_tasks = self.db.query(Execution).filter(
            Execution.agent_id == agent.id
        ).count()

        completed_tasks = self.db.query(Execution).filter(
            Execution.agent_id == agent.id,
            Execution.status == ExecutionStatus.completed.value
        ).count()

        failed_tasks = self.db.query(Execution).filter(
            Execution.agent_id == agent.id,
            Execution.status == ExecutionStatus.failed.value
        ).count()

        return {
            "agent_id": agent.id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
        }

    def get_agent_performance(self, agent: Agent, days: int = 30) -> dict:
        """Get agent performance summary (T-324)"""
        from datetime import datetime, timezone, timedelta
        from schemas.agent import AgentPerformanceResponse

        start_date = datetime.now(timezone.utc).date() - timedelta(days=days)

        metrics = self.db.query(AgentMetric).filter(
            AgentMetric.agent_id == agent.id,
            AgentMetric.date >= start_date
        ).all()

        tasks_completed = sum(m.tasks_completed for m in metrics)
        tasks_failed = sum(m.tasks_failed for m in metrics)
        total_tasks = tasks_completed + tasks_failed
        success_rate = (tasks_completed / total_tasks * 100) if total_tasks > 0 else 0.0

        avg_response_time_ms = 0
        if metrics:
            avg_response_time_ms = int(sum(m.avg_response_time_ms for m in metrics) / len(metrics))

        total_token_usage = sum(m.token_usage for m in metrics)

        is_healthy = agent.status in ("online", "busy")
        uptime_seconds = 3600 if agent.status == "online" else (7200 if agent.status == "busy" else 0)

        return AgentPerformanceResponse(
            agent_id=agent.id,
            status=agent.status,
            is_healthy=is_healthy,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            success_rate=round(success_rate, 2),
            avg_response_time_ms=avg_response_time_ms,
            total_token_usage=total_token_usage,
            uptime_seconds=uptime_seconds,
            last_seen_at=agent.updated_at,
        ).model_dump()

    def get_org_agents_usage(self, org_id: str, days: int = 30) -> dict:
        """Get aggregated usage for all agents in an org (T-323)"""
        from datetime import datetime, timezone, timedelta
        from schemas.agent import OrgAgentsUsageResponse, OrgAgentUsageEntry

        start_date = datetime.now(timezone.utc).date() - timedelta(days=days)

        agents = self.get_org_agents(org_id)

        agent_usages = []
        total_tasks_completed = 0
        total_tasks_failed = 0
        total_token_usage = 0
        total_response_time = 0
        active_agents = 0

        for agent in agents:
            metrics = self.db.query(AgentMetric).filter(
                AgentMetric.agent_id == agent.id,
                AgentMetric.date >= start_date
            ).all()

            agent_tasks_completed = sum(m.tasks_completed for m in metrics)
            agent_tasks_failed = sum(m.tasks_failed for m in metrics)
            agent_token_usage = sum(m.token_usage for m in metrics)
            agent_avg_response = int(sum(m.avg_response_time_ms for m in metrics) / len(m)) if metrics else 0

            agent_usages.append(OrgAgentUsageEntry(
                agent_id=agent.id,
                agent_name=agent.name,
                tasks_completed=agent_tasks_completed,
                tasks_failed=agent_tasks_failed,
                avg_response_time_ms=agent_avg_response,
                token_usage=agent_token_usage,
            ))

            total_tasks_completed += agent_tasks_completed
            total_tasks_failed += agent_tasks_failed
            total_token_usage += agent_token_usage
            if metrics:
                total_response_time += agent_avg_response
            if agent.status in ("online", "busy"):
                active_agents += 1

        avg_response_time_ms = int(total_response_time / len(agents)) if agents else 0

        return OrgAgentsUsageResponse(
            org_id=org_id,
            total_agents=len(agents),
            active_agents=active_agents,
            total_tasks_completed=total_tasks_completed,
            total_tasks_failed=total_tasks_failed,
            avg_response_time_ms=avg_response_time_ms,
            total_token_usage=total_token_usage,
            agent_usages=agent_usages,
        ).model_dump()
