from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.project import Project
from models.task import Task
from models.agent import Agent
from models.activity import Activity
from models.organization import OrganizationMember

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def api_response(code=0, message="success", data=None):
    return {"code": code, "message": message, "data": data}


def get_org_id_from_user(db: Session, user: User) -> str | None:
    """Get the first org_id the user belongs to."""
    member = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == user.id
    ).first()
    return member.org_id if member else None


@router.get("/stats", response_model=dict)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取仪表盘统计数据"""
    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        return api_response(data={
            "project_count": 0,
            "task_count": 0,
            "agent_count": 0,
            "completed_today": 0,
        })

    # 项目数
    project_count = db.query(Project).filter(Project.org_id == org_id).count()

    # 任务数（进行中）- via project
    task_count = db.query(Task).join(Project).filter(
        Project.org_id == org_id,
        Task.status.in_(["pending", "in_progress"])
    ).count()

    # Agent 数
    agent_count = db.query(Agent).filter(Agent.org_id == org_id).count()

    # 完成的任务数（今日）
    from datetime import datetime, timezone
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = db.query(Task).join(Project).filter(
        Project.org_id == org_id,
        Task.status == "completed",
        Task.completed_at >= today_start
    ).count()

    return api_response(data={
        "project_count": project_count,
        "task_count": task_count,
        "agent_count": agent_count,
        "completed_today": completed_today,
    })

@router.get("/task-trend", response_model=dict)
def get_task_trend(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务完成趋势（最近N天）"""
    from datetime import datetime, timezone, timedelta
    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        return api_response(data=[])

    trend = []
    for i in range(days):
        day = datetime.now(timezone.utc).date() - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(day, datetime.max.time()).replace(tzinfo=timezone.utc)

        count = db.query(Task).join(Project).filter(
            Project.org_id == org_id,
            Task.status == "completed",
            Task.completed_at >= day_start,
            Task.completed_at <= day_end
        ).count()
        trend.append({"date": day.isoformat(), "count": count})

    trend.reverse()
    return api_response(data=trend)

@router.get("/recent-activities", response_model=dict)
def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取最近活动"""
    activities = db.query(Activity).filter(
        Activity.tenant_id == current_user.tenant_id
    ).order_by(desc(Activity.created_at)).limit(limit).all()

    return api_response(data=[
        {
            "id": a.id,
            "actor_name": a.actor_name,
            "action_type": a.action_type,
            "entity_type": a.entity_type,
            "entity_name": a.entity_name,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in activities
    ])


@router.get("/chart/agents-tasks", response_model=dict)
def get_agents_tasks_chart(
    days: int = Query(7, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取 Agent 完成任务趋势图表数据"""
    from datetime import datetime, timezone, timedelta
    from models.execution import Execution

    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        return api_response(data={"labels": [], "datasets": []})

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # 获取所有 agent
    agents = db.query(Agent).filter(Agent.org_id == org_id).all()

    # 生成日期标签
    labels = []
    for i in range(days):
        day = (end_date - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        labels.append(day)

    # 对每个 agent 计算每天的任务数
    datasets = []
    for agent in agents:
        agent_data = []
        for i in range(days):
            day_start = datetime.combine((end_date - timedelta(days=days - 1 - i)).date(), datetime.min.time()).replace(tzinfo=timezone.utc)
            day_end = datetime.combine((end_date - timedelta(days=days - 1 - i)).date(), datetime.max.time()).replace(tzinfo=timezone.utc)
            count = db.query(Execution).filter(
                Execution.agent_id == agent.id,
                Execution.status == 'completed',
                Execution.created_at >= day_start,
                Execution.created_at <= day_end
            ).count()
            agent_data.append(count)
        datasets.append({
            "agent_id": agent.id,
            "agent_name": agent.name or agent.id,
            "data": agent_data
        })

    return api_response(data={"labels": labels, "datasets": datasets})


@router.get("/chart/task-completion", response_model=dict)
def get_task_completion_chart(
    days: int = Query(7, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务完成趋势图表数据"""
    from datetime import datetime, timezone, timedelta

    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        return api_response(data={"labels": [], "completed": [], "failed": []})

    end_date = datetime.now(timezone.utc)

    labels = []
    completed = []
    failed = []

    for i in range(days):
        day = (end_date - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        labels.append(day)
        day_start = datetime.combine((end_date - timedelta(days=days - 1 - i)).date(), datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = datetime.combine((end_date - timedelta(days=days - 1 - i)).date(), datetime.max.time()).replace(tzinfo=timezone.utc)

        comp = db.query(Task).join(Project).filter(
            Project.org_id == org_id,
            Task.status == "completed",
            Task.completed_at >= day_start,
            Task.completed_at <= day_end
        ).count()
        fail = db.query(Task).join(Project).filter(
            Project.org_id == org_id,
            Task.status == "failed",
            Task.completed_at >= day_start,
            Task.completed_at <= day_end
        ).count()
        completed.append(comp)
        failed.append(fail)

    return api_response(data={"labels": labels, "completed": completed, "failed": failed})


@router.get("/chart/activity-heatmap", response_model=dict)
def get_activity_heatmap(
    days: int = Query(7, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取活动热力图数据"""
    from datetime import datetime, timezone, timedelta

    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        return api_response(data={"days": [], "hours": list(range(24)), "values": []})

    end_date = datetime.now(timezone.utc)

    days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))
    values = [[0] * 24 for _ in range(7)]

    activities = db.query(Activity).filter(
        Activity.tenant_id == current_user.tenant_id,
        Activity.created_at >= end_date - timedelta(days=days)
    ).all()

    for activity in activities:
        if activity.created_at:
            weekday = activity.created_at.weekday()  # 0=Monday
            hour = activity.created_at.hour
            values[weekday][hour] += 1

    return api_response(data={"days": days_labels, "hours": hours, "values": values})