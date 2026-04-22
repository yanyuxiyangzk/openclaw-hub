import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.scheduler_job import SchedulerJob
from models.task import Task
from models.agent import Agent
from models.project import Project
from models.project_member import ProjectMember
from models.user import User
from schemas.scheduler_job import SchedulerJobCreate, SchedulerJobUpdate


class SchedulerService:
    def __init__(self, db: Session):
        self.db = db

    def _get_job_or_404(self, job_id: str) -> SchedulerJob:
        job = self.db.query(SchedulerJob).filter(SchedulerJob.id == job_id).first()
        if not job:
            raise ValueError("Scheduled job not found")
        return job

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

    def _calculate_next_run(self, cron_expression: str) -> Optional[datetime]:
        from croniter import croniter
        try:
            cron = croniter(cron_expression, datetime.now(timezone.utc))
            return cron.get_next(datetime)
        except (ValueError, KeyError):
            return None

    def create_job(self, data: SchedulerJobCreate, user: User) -> SchedulerJob:
        task = self._get_task_or_404(data.task_template_id)
        agent = self._get_agent_or_404(data.agent_id)

        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        next_run = self._calculate_next_run(data.cron_expression)

        job = SchedulerJob(
            name=data.name,
            task_template_id=data.task_template_id,
            cron_expression=data.cron_expression,
            agent_id=data.agent_id,
            enabled=data.enabled,
            next_run_at=next_run,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_jobs(self, user: User) -> tuple[list[SchedulerJob], int]:
        jobs = self.db.query(SchedulerJob).order_by(desc(SchedulerJob.created_at)).all()

        filtered = []
        for j in jobs:
            task = self._get_task_or_404(j.task_template_id)
            if self._check_task_access(task, user):
                filtered.append(j)

        return filtered, len(filtered)

    def get_job(self, job_id: str, user: User) -> SchedulerJob:
        job = self._get_job_or_404(job_id)
        task = self._get_task_or_404(job.task_template_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this scheduled job")
        return job

    def delete_job(self, job_id: str, user: User) -> None:
        job = self._get_job_or_404(job_id)
        task = self._get_task_or_404(job.task_template_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this scheduled job")

        self.db.delete(job)
        self.db.commit()

    def get_job_runs(self, job_id: str, user: User) -> tuple[list[dict], int]:
        job = self._get_job_or_404(job_id)
        task = self._get_task_or_404(job.task_template_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this scheduled job")

        from models.execution import Execution
        executions = self.db.query(Execution).filter(
            Execution.task_id == job.task_template_id,
            Execution.agent_id == job.agent_id
        ).order_by(desc(Execution.created_at)).limit(50).all()

        runs = [{
            "execution_id": e.id,
            "status": e.status,
            "started_at": e.started_at,
            "completed_at": e.completed_at,
            "created_at": e.created_at,
        } for e in executions]

        return runs, len(runs)

    def update_job(self, job_id: str, data: SchedulerJobUpdate, user: User) -> SchedulerJob:
        job = self._get_job_or_404(job_id)
        task = self._get_task_or_404(job.task_template_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this scheduled job")

        if data.name is not None:
            job.name = data.name
        if data.cron_expression is not None:
            job.cron_expression = data.cron_expression
            job.next_run_at = self._calculate_next_run(data.cron_expression)
        if data.agent_id is not None:
            job.agent_id = data.agent_id
        if data.enabled is not None:
            job.enabled = data.enabled

        self.db.commit()
        self.db.refresh(job)
        return job
