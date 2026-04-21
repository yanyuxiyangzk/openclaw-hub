from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.agent import Agent
from models.organization import OrganizationMember
from schemas.agent_role import (
    AgentRoleCreate, AgentRoleUpdate, AgentRoleResponse,
    AgentSkillBindRequest, AgentSkillUpdate, AgentSkillResponse,
    AgentMemoryConfig, AgentMemoryResponse, AgentContextRequest,
    AgentHistoryResponse, AgentMetricsResponse, AgentDailyStatsResponse,
    AgentTaskCountResponse, OrgAgentUsageResponse, AgentPerformanceResponse,
    AgentHealthDetailResponse
)
from services.phase3_service import Phase3Service
from datetime import date

router = APIRouter(prefix="/api", tags=["phase3"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_org_id_from_user(db: Session, user: User) -> str | None:
    member = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == user.id
    ).first()
    return member.org_id if member else None


def get_agent_or_404(db: Session, agent_id: str) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Agent not found"}
        )
    return agent


def check_agent_access(db: Session, agent: Agent, user: User):
    org_id = get_org_id_from_user(db, user)
    if not org_id or agent.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )


# ========== Agent Roles (T-301 ~ T-308) ==========

@router.get("/agent-roles", response_model=dict)
def list_agent_roles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agent-roles - List roles (T-301)"""
    org_id = get_org_id_from_user(db, current_user)
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "User does not belong to any organization"}
        )
    service = Phase3Service(db)
    roles = service.get_org_roles(org_id)
    return response(data=[AgentRoleResponse.model_validate(r).model_dump() for r in roles])


@router.post("/agent-roles", response_model=dict)
def create_agent_role(data: AgentRoleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agent-roles - Create role (T-302)"""
    service = Phase3Service(db)
    role = service.create_role(data, current_user)
    return response(data=AgentRoleResponse.model_validate(role).model_dump())


@router.get("/agent-roles/{role_id}", response_model=dict)
def get_agent_role(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agent-roles/{id} - Get role (T-303)"""
    service = Phase3Service(db)
    role = service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Role not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if role.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )
    return response(data=AgentRoleResponse.model_validate(role).model_dump())


@router.put("/agent-roles/{role_id}", response_model=dict)
def update_agent_role(role_id: str, data: AgentRoleUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/agent-roles/{id} - Update role (T-304)"""
    service = Phase3Service(db)
    role = service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Role not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if role.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    role = service.update_role(role, data)
    return response(data=AgentRoleResponse.model_validate(role).model_dump())


@router.delete("/agent-roles/{role_id}", response_model=dict)
def delete_agent_role(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/agent-roles/{id} - Delete role (T-305)"""
    service = Phase3Service(db)
    role = service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Role not found"}
        )

    org_id = get_org_id_from_user(db, current_user)
    if role.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    service.delete_role(role)
    return response(message="Role deleted successfully")


@router.post("/agents/{agent_id}/skills", response_model=dict)
def bind_agent_skill(agent_id: str, data: AgentSkillBindRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents/{id}/skills - Bind skill (T-306)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    skill = service.bind_skill_to_agent(agent, data)
    return response(data=AgentSkillResponse.model_validate(skill).model_dump())


@router.delete("/agents/{agent_id}/skills/{skill_id}", response_model=dict)
def unbind_agent_skill(agent_id: str, skill_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/agents/{id}/skills/{skill_id} - Unbind skill (T-307)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    skill = service.get_skill_by_id(skill_id)
    if not skill or skill.agent_id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "Skill not found"}
        )

    service.unbind_skill(skill)
    return response(message="Skill unbound successfully")


@router.get("/agents/{agent_id}/skills", response_model=dict)
def list_agent_skills(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/skills - List agent skills (T-308)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    skills = service.get_agent_skills(agent_id)
    return response(data=[AgentSkillResponse.model_validate(s).model_dump() for s in skills])


# ========== Agent Memory (T-310 ~ T-315) ==========

@router.get("/agents/{agent_id}/memory", response_model=dict)
def get_agent_memory(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/memory - Get memory config (T-310)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    memory = service.get_agent_memory_config(agent)
    return response(data=memory)


@router.put("/agents/{agent_id}/memory", response_model=dict)
def update_agent_memory(agent_id: str, data: AgentMemoryConfig, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/agents/{id}/memory - Update memory config (T-311)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    memory = service.update_agent_memory_config(agent, data)
    return response(data=memory)


@router.post("/agents/{agent_id}/context", response_model=dict)
def set_agent_context(agent_id: str, data: AgentContextRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents/{id}/context - Set context (T-312)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    result = service.set_agent_context(agent, data)
    return response(data=result)


@router.get("/agents/{agent_id}/history", response_model=dict)
def get_agent_history(agent_id: str, limit: int = Query(50, ge=1, le=200), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/history - Get conversation history (T-313)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    history = service.get_agent_history(agent, limit)
    return response(data=history)


@router.delete("/agents/{agent_id}/memory/clear", response_model=dict)
def clear_agent_memory(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DELETE /api/agents/{id}/memory/clear - Clear memory (T-314)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    result = service.clear_agent_memory(agent)
    return response(data=result)


@router.post("/agents/{agent_id}/reset", response_model=dict)
def reset_agent_state(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """POST /api/agents/{id}/reset - Reset agent state (T-315)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    result = service.reset_agent_state(agent)
    return response(data=result)


# ========== Agent Metrics (T-320 ~ T-325) ==========

@router.get("/agents/{agent_id}/metrics", response_model=dict)
def get_agent_metrics(agent_id: str, days: int = Query(7, ge=1, le=90), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/metrics - Get metrics (T-320)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    metrics = service.get_agent_metrics(agent_id, days)
    return response(data=[AgentMetricsResponse.model_validate(m).model_dump() for m in metrics])


@router.get("/agents/{agent_id}/metrics/daily", response_model=dict)
def get_agent_daily_stats(agent_id: str, start_date: date = Query(...), end_date: date = Query(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/metrics/daily - Get daily stats (T-321)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    metrics = service.get_agent_daily_stats(agent_id, start_date, end_date)
    return response(data=[AgentDailyStatsResponse.model_validate(m).model_dump() for m in metrics])


@router.get("/agents/{agent_id}/tasks/count", response_model=dict)
def get_agent_task_counts(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/tasks/count - Get task counts (T-322)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    counts = service.get_agent_task_counts(agent_id)
    return response(data=counts)


@router.get("/orgs/{org_id}/agents/usage", response_model=dict)
def get_org_agent_usage(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/orgs/{id}/agents/usage - Get org agent usage (T-323)"""
    org_id_from_user = get_org_id_from_user(db, current_user)
    if org_id != org_id_from_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )

    service = Phase3Service(db)
    usage = service.get_org_agent_usage(org_id)
    return response(data=usage)


@router.get("/agents/{agent_id}/performance", response_model=dict)
def get_agent_performance(agent_id: str, days: int = Query(7, ge=1, le=90), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/performance - Get performance report (T-324)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    perf = service.get_agent_performance(agent, days)
    return response(data=perf)


@router.get("/agents/{agent_id}/health", response_model=dict)
def get_agent_health_detail(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/agents/{id}/health - Get agent health (T-325)"""
    agent = get_agent_or_404(db, agent_id)
    check_agent_access(db, agent, current_user)

    service = Phase3Service(db)
    health = service.get_agent_health_detail(agent)
    return response(data=health)