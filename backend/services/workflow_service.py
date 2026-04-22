import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.workflow import Workflow
from models.organization import Organization, OrganizationMember
from models.task import Task
from models.agent import Agent
from models.execution import Execution, ExecutionStatus
from models.user import User
from schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowExecuteRequest


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def _get_workflow_or_404(self, workflow_id: str) -> Workflow:
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError("Workflow not found")
        return workflow

    def _get_org_or_404(self, org_id: str) -> Organization:
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError("Organization not found")
        return org

    def _get_task_or_404(self, task_id: str) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        return task

    def _get_agent_or_404(self, agent_id: str) -> Agent:
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise ValueError("Agent not found")
        return agent

    def _is_org_member(self, org_id: str, user: User) -> bool:
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user.id
        ).first()
        return member is not None

    def _parse_json_field(self, data: Optional[str]) -> Optional[dict]:
        if data is None:
            return None
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return None

    def _serialize_json_field(self, data: Optional[dict]) -> Optional[str]:
        if data is None:
            return None
        return json.dumps(data)

    def create_workflow(self, data: WorkflowCreate, user: User) -> Workflow:
        if not data.steps:
            raise ValueError("Workflow must have at least one step")

        # Get org_id from the first task's project
        first_task = self._get_task_or_404(data.steps[0].task_template_id)
        from models.project import Project
        project = self.db.query(Project).filter(Project.id == first_task.project_id).first()
        if not project:
            raise ValueError("Task's project not found")

        if not self._is_org_member(project.org_id, user):
            raise PermissionError("Access denied to this organization")

        steps_json = json.dumps([s.model_dump() for s in data.steps])

        workflow = Workflow(
            name=data.name,
            description=data.description,
            steps=steps_json,
            org_id=project.org_id,
            created_by=user.id,
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def get_workflow(self, workflow_id: str, user: User) -> Workflow:
        workflow = self._get_workflow_or_404(workflow_id)
        if not self._is_org_member(workflow.org_id, user):
            raise PermissionError("Access denied to this workflow")
        return workflow

    def get_workflows(self, org_id: Optional[str], user: User) -> tuple[list[Workflow], int]:
        query = self.db.query(Workflow)
        if org_id:
            query = query.filter(Workflow.org_id == org_id)

        workflows = query.order_by(desc(Workflow.created_at)).all()

        filtered = [w for w in workflows if self._is_org_member(w.org_id, user)]

        return filtered, len(filtered)

    def update_workflow(self, workflow_id: str, data: WorkflowUpdate, user: User) -> Workflow:
        workflow = self._get_workflow_or_404(workflow_id)
        if not self._is_org_member(workflow.org_id, user):
            raise PermissionError("Access denied to this workflow")

        if data.name is not None:
            workflow.name = data.name
        if data.description is not None:
            workflow.description = data.description
        if data.steps is not None:
            workflow.steps = json.dumps([s.model_dump() for s in data.steps])

        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def delete_workflow(self, workflow_id: str, user: User) -> None:
        workflow = self._get_workflow_or_404(workflow_id)
        if not self._is_org_member(workflow.org_id, user):
            raise PermissionError("Access denied to this workflow")

        self.db.delete(workflow)
        self.db.commit()

    def execute_workflow(self, workflow_id: str, data: WorkflowExecuteRequest, user: User) -> list[Execution]:
        workflow = self._get_workflow_or_404(workflow_id)
        if not self._is_org_member(workflow.org_id, user):
            raise PermissionError("Access denied to this workflow")

        steps = self._parse_json_field(workflow.steps)
        if not steps:
            raise ValueError("Workflow has no steps")

        executions = []
        for step in steps:
            task_id = step.get("task_template_id")
            agent_id = data.agent_id or step.get("agent_id")

            if not agent_id:
                raise ValueError(f"Agent not specified for step {step.get('step_id')}")

            task = self._get_task_or_404(task_id)
            agent = self._get_agent_or_404(agent_id)

            execution = Execution(
                task_id=task_id,
                agent_id=agent_id,
                status=ExecutionStatus.pending.value,
                input_data=self._serialize_json_field(data.input_data),
            )
            self.db.add(execution)
            executions.append(execution)

        self.db.commit()
        for e in executions:
            self.db.refresh(e)

        return executions
