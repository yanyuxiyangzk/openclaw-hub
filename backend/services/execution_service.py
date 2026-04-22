import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.execution import Execution, ExecutionStatus
from models.task import Task
from models.agent import Agent
from models.project import Project
from models.project_member import ProjectMember
from models.user import User
from schemas.execution import ExecutionCreate


class ExecutionService:
    def __init__(self, db: Session):
        self.db = db

    def _get_execution_or_404(self, execution_id: str) -> Execution:
        execution = self.db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            raise ValueError("Execution not found")
        return execution

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

    def _check_project_access(self, project_id: str, user: User) -> bool:
        member = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        ).first()
        return member is not None

    def _check_task_access(self, task: Task, user: User) -> bool:
        return self._check_project_access(task.project_id, user)

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

    def create_execution(self, data: ExecutionCreate, user: User) -> Execution:
        task = self._get_task_or_404(data.task_id)
        agent = self._get_agent_or_404(data.agent_id)

        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        execution = Execution(
            task_id=data.task_id,
            agent_id=data.agent_id,
            status=ExecutionStatus.pending.value,
            input_data=self._serialize_json_field(data.input_data),
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get_execution(self, execution_id: str, user: User) -> Execution:
        execution = self._get_execution_or_404(execution_id)
        task = self._get_task_or_404(execution.task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this execution")
        return execution

    def get_task_executions(self, task_id: str, user: User) -> tuple[list[Execution], int]:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        executions = self.db.query(Execution).filter(
            Execution.task_id == task_id
        ).order_by(desc(Execution.created_at)).all()

        return executions, len(executions)

    def cancel_execution(self, execution_id: str, user: User) -> Execution:
        execution = self._get_execution_or_404(execution_id)
        task = self._get_task_or_404(execution.task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this execution")

        if execution.status not in [ExecutionStatus.pending.value, ExecutionStatus.running.value]:
            raise ValueError("Cannot cancel execution in current state")

        execution.status = ExecutionStatus.cancelled.value
        execution.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def retry_execution(self, execution_id: str, user: User) -> Execution:
        execution = self._get_execution_or_404(execution_id)
        task = self._get_task_or_404(execution.task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this execution")

        if execution.status not in [ExecutionStatus.failed.value, ExecutionStatus.cancelled.value]:
            raise ValueError("Cannot retry execution in current state")

        new_execution = Execution(
            task_id=execution.task_id,
            agent_id=execution.agent_id,
            status=ExecutionStatus.pending.value,
            input_data=execution.input_data,
        )
        self.db.add(new_execution)
        self.db.commit()
        self.db.refresh(new_execution)
        return new_execution

    def get_execution_output(self, execution_id: str, user: User) -> dict:
        execution = self._get_execution_or_404(execution_id)
        task = self._get_task_or_404(execution.task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this execution")

        return {
            "id": execution.id,
            "output_data": self._parse_json_field(execution.output_data),
            "status": execution.status,
        }

    def get_active_executions(self, user: User) -> tuple[list[Execution], int]:
        executions = self.db.query(Execution).filter(
            Execution.status.in_([ExecutionStatus.pending.value, ExecutionStatus.running.value])
        ).order_by(desc(Execution.created_at)).all()

        filtered = []
        for e in executions:
            task = self._get_task_or_404(e.task_id)
            if self._check_task_access(task, user):
                filtered.append(e)

        return filtered, len(filtered)

    def start_execution(self, execution_id: str) -> Execution:
        execution = self._get_execution_or_404(execution_id)
        execution.status = ExecutionStatus.running.value
        execution.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def complete_execution(self, execution_id: str, output_data: Optional[dict] = None, error_message: Optional[str] = None) -> Execution:
        execution = self._get_execution_or_404(execution_id)
        execution.status = ExecutionStatus.completed.value if not error_message else ExecutionStatus.failed.value
        execution.completed_at = datetime.now(timezone.utc)
        execution.output_data = self._serialize_json_field(output_data)
        execution.error_message = error_message
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def batch_execute(self, task_ids: list[str], agent_id: str, user: User) -> list[Execution]:
        agent = self._get_agent_or_404(agent_id)
        executions = []

        for task_id in task_ids:
            task = self._get_task_or_404(task_id)
            if not self._check_task_access(task, user):
                continue

            execution = Execution(
                task_id=task_id,
                agent_id=agent_id,
                status=ExecutionStatus.pending.value,
            )
            self.db.add(execution)
            executions.append(execution)

        self.db.commit()
        for e in executions:
            self.db.refresh(e)

        return executions
