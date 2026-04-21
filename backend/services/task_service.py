import json
import csv
import io
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models.task import Task, TaskStatus, TaskPriority
from models.task_comment import TaskComment
from models.task_attachment import TaskAttachment
from models.project import Project
from models.project_member import ProjectMember
from models.user import User
from schemas.task import (
    TaskCreate, TaskUpdate, TaskBulkCreate, TaskBulkStatusUpdate,
    TaskMoveRequest, TaskAssignRequest, TaskCommentCreate,
    ReminderRequest, SnoozeRequest
)


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def _get_task_or_404(self, task_id: str) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        return task

    def _get_project_or_404(self, project_id: str) -> Project:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        return project

    def _check_project_access(self, project_id: str, user: User) -> bool:
        member = self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        ).first()
        return member is not None

    def _check_task_access(self, task: Task, user: User) -> bool:
        return self._check_project_access(task.project_id, user)

    def _serialize_tags(self, tags: Optional[list[str]]) -> Optional[str]:
        if tags is None:
            return None
        return json.dumps(tags)

    def _deserialize_tags(self, tags_str: Optional[str]) -> Optional[list[str]]:
        if tags_str is None:
            return None
        try:
            return json.loads(tags_str)
        except (json.JSONDecodeError, TypeError):
            return None

    # ========== Task CRUD ==========

    def create_task(self, data: TaskCreate, user: User) -> Task:
        project = self._get_project_or_404(data.project_id)
        if not self._check_project_access(data.project_id, user):
            raise PermissionError("Access denied to this project")

        task = Task(
            title=data.title,
            description=data.description,
            project_id=data.project_id,
            status=data.status,
            priority=data.priority,
            parent_id=data.parent_id,
            root_id=data.root_id,
            position=data.position,
            estimated_hours=data.estimated_hours,
            actual_hours=data.actual_hours,
            tags=self._serialize_tags(data.tags),
            due_date=data.due_date,
            reminder_at=data.reminder_at,
            assignee_id=data.assignee_id,
            created_by=user.id
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: str, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")
        return task

    def update_task(self, task_id: str, data: TaskUpdate, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        update_data = data.model_dump(exclude_unset=True)
        if "tags" in update_data:
            update_data["tags"] = self._serialize_tags(update_data["tags"])

        for key, value in update_data.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: str, user: User) -> None:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")
        self.db.delete(task)
        self.db.commit()

    def list_tasks(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[str] = None,
        user: Optional[User] = None
    ) -> tuple[list[Task], int]:
        query = self.db.query(Task)

        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        if priority:
            query = query.filter(Task.priority == priority)

        query = query.filter(Task.parent_id.is_(None))
        query = query.order_by(Task.position.asc(), Task.created_at.desc())

        total = query.count()
        tasks = query.all()
        return tasks, total

    def bulk_create_tasks(self, data: TaskBulkCreate, user: User) -> list[Task]:
        tasks = []
        for task_data in data.tasks:
            task = self.create_task(task_data, user)
            tasks.append(task)
        return tasks

    def bulk_update_status(self, data: TaskBulkStatusUpdate, user: User) -> list[Task]:
        tasks = []
        for task_id in data.task_ids:
            task = self._get_task_or_404(task_id)
            if self._check_task_access(task, user):
                task.status = data.status
                tasks.append(task)
        self.db.commit()
        return tasks

    def export_tasks(
        self,
        project_id: str,
        format: str = "json",
        user: User = None
    ) -> str:
        if not self._check_project_access(project_id, user):
            raise PermissionError("Access denied to this project")

        tasks, _ = self.list_tasks(project_id=project_id)

        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "id", "title", "description", "status", "priority",
                "assignee_id", "due_date", "estimated_hours", "actual_hours",
                "created_at", "updated_at"
            ])
            for task in tasks:
                writer.writerow([
                    task.id, task.title, task.description, task.status, task.priority,
                    task.assignee_id, task.due_date, task.estimated_hours,
                    task.actual_hours, task.created_at, task.updated_at
                ])
            return output.getvalue()
        else:
            result = []
            for task in tasks:
                result.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assignee_id": task.assignee_id,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "estimated_hours": task.estimated_hours,
                    "actual_hours": task.actual_hours,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                })
            return json.dumps(result, indent=2)

    # ========== Task Collaboration ==========

    def assign_task(self, task_id: str, data: TaskAssignRequest, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")
        task.assignee_id = data.assignee_id
        self.db.commit()
        self.db.refresh(task)
        return task

    def claim_task(self, task_id: str, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")
        task.assignee_id = user.id
        self.db.commit()
        self.db.refresh(task)
        return task

    def complete_task(self, task_id: str, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")
        task.status = TaskStatus.done.value
        task.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
        return task

    # ========== Comments ==========

    def add_comment(self, task_id: str, data: TaskCommentCreate, user: User) -> TaskComment:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        comment = TaskComment(
            task_id=task_id,
            user_id=user.id,
            content=data.content
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments(self, task_id: str, user: User) -> tuple[list[TaskComment], int]:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        comments = self.db.query(TaskComment).filter(
            TaskComment.task_id == task_id
        ).order_by(TaskComment.created_at.asc()).all()

        return comments, len(comments)

    # ========== Subtasks ==========

    def create_subtask(self, parent_id: str, data: TaskCreate, user: User) -> Task:
        parent = self._get_task_or_404(parent_id)
        if not self._check_task_access(parent, user):
            raise PermissionError("Access denied to this task")

        data.parent_id = parent_id
        data.root_id = parent.root_id or parent.id
        data.project_id = parent.project_id

        return self.create_task(data, user)

    def get_subtasks(self, parent_id: str, user: User) -> tuple[list[Task], int]:
        parent = self._get_task_or_404(parent_id)
        if not self._check_task_access(parent, user):
            raise PermissionError("Access denied to this task")

        subtasks = self.db.query(Task).filter(
            Task.parent_id == parent_id
        ).order_by(Task.position.asc()).all()

        return subtasks, len(subtasks)

    # ========== Attachments ==========

    def add_attachment(
        self,
        task_id: str,
        filename: str,
        file_url: str,
        file_size: int,
        user: User
    ) -> TaskAttachment:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        attachment = TaskAttachment(
            task_id=task_id,
            filename=filename,
            file_url=file_url,
            file_size=file_size,
            uploaded_by=user.id
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def get_attachments(self, task_id: str, user: User) -> tuple[list[TaskAttachment], int]:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        attachments = self.db.query(TaskAttachment).filter(
            TaskAttachment.task_id == task_id
        ).order_by(TaskAttachment.uploaded_at.desc()).all()

        return attachments, len(attachments)

    # ========== Kanban Views ==========

    def get_kanban_board(self, project_id: str, user: User) -> dict:
        if not self._check_project_access(project_id, user):
            raise PermissionError("Access denied to this project")

        statuses = [s.value for s in TaskStatus]
        columns = []

        for status in statuses:
            tasks, _ = self.list_tasks(project_id=project_id, status=status)
            columns.append({
                "status": status,
                "tasks": tasks,
                "count": len(tasks)
            })

        total = self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.parent_id.is_(None)
        ).count()

        return {"columns": columns, "total": total}

    def get_tasks_by_status(self, project_id: str, user: User) -> dict:
        if not self._check_project_access(project_id, user):
            raise PermissionError("Access denied to this project")

        result = {}
        for status in TaskStatus:
            tasks, _ = self.list_tasks(project_id=project_id, status=status.value)
            result[status.value] = tasks

        return result

    def get_tasks_by_assignee(self, project_id: str, user: User) -> dict:
        if not self._check_project_access(project_id, user):
            raise PermissionError("Access denied to this project")

        tasks = self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.parent_id.is_(None)
        ).all()

        result = {}
        for task in tasks:
            assignee_id = task.assignee_id or "unassigned"
            if assignee_id not in result:
                result[assignee_id] = []
            result[assignee_id].append(task)

        return result

    def get_timeline(self, project_id: str, user: User) -> list[Task]:
        if not self._check_project_access(project_id, user):
            raise PermissionError("Access denied to this project")

        tasks = self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.parent_id.is_(None),
            Task.due_date.isnot(None)
        ).order_by(Task.due_date.asc()).all()

        return tasks

    def move_task(self, task_id: str, data: TaskMoveRequest, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        if data.status is not None:
            task.status = data.status
        if data.position is not None:
            task.position = data.position
        if data.assignee_id is not None:
            task.assignee_id = data.assignee_id

        self.db.commit()
        self.db.refresh(task)
        return task

    def get_activity(self, task_id: str, user: User) -> list[dict]:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        activities = []

        comments = self.db.query(TaskComment).filter(
            TaskComment.task_id == task_id
        ).all()
        for c in comments:
            activities.append({
                "id": c.id,
                "task_id": task_id,
                "user_id": c.user_id,
                "action": "commented",
                "old_value": None,
                "new_value": c.content[:100],
                "created_at": c.created_at,
                "user_email": c.author.email if c.author else None,
                "user_name": c.author.name if c.author else None
            })

        activities.sort(key=lambda x: x["created_at"], reverse=True)
        return activities

    # ========== Reminders ==========

    def set_reminder(self, task_id: str, data: ReminderRequest, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        task.reminder_at = data.reminder_at
        self.db.commit()
        self.db.refresh(task)
        return task

    def snooze_reminder(self, task_id: str, data: SnoozeRequest, user: User) -> Task:
        task = self._get_task_or_404(task_id)
        if not self._check_task_access(task, user):
            raise PermissionError("Access denied to this task")

        if task.reminder_at:
            new_reminder = task.reminder_at + timedelta(minutes=data.snooze_minutes)
        else:
            new_reminder = datetime.now(timezone.utc) + timedelta(minutes=data.snooze_minutes)

        task.reminder_at = new_reminder
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_due_soon_tasks(self, user: User, hours: int = 24) -> dict:
        now = datetime.now(timezone.utc)
        threshold = now + timedelta(hours=hours)

        tasks = self.db.query(Task).filter(
            Task.assignee_id == user.id,
            Task.reminder_at.isnot(None),
            Task.reminder_at <= threshold,
            Task.status != TaskStatus.done.value
        ).all()

        overdue = [t for t in tasks if t.due_date and t.due_date < now]
        due_today = [t for t in tasks if t.due_date and t.due_date.date() == now.date()]
        due_this_week = [
            t for t in tasks
            if t.due_date and t.due_date.date() >= now.date()
            and t.due_date.date() <= (now + timedelta(days=7)).date()
        ]

        return {
            "tasks": tasks,
            "total": len(tasks),
            "overdue": len(overdue),
            "due_today": len(due_today),
            "due_this_week": len(due_this_week)
        }
