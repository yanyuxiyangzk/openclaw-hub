from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.scheduler_job import (
    SchedulerJobCreate, SchedulerJobUpdate, SchedulerJobResponse, SchedulerJobListResponse
)
from services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_scheduler_service(db: Session = Depends(get_db)) -> SchedulerService:
    return SchedulerService(db)


def _job_to_response(job) -> dict:
    return {
        "id": job.id,
        "name": job.name,
        "task_template_id": job.task_template_id,
        "cron_expression": job.cron_expression,
        "agent_id": job.agent_id,
        "enabled": job.enabled,
        "last_run_at": job.last_run_at,
        "next_run_at": job.next_run_at,
        "created_at": job.created_at,
    }


@router.post("/jobs", response_model=dict)
def create_job(
    data: SchedulerJobCreate,
    current_user: User = Depends(get_current_user),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """POST /api/scheduler/jobs - Create scheduled task (T-510)"""
    try:
        job = service.create_job(data, current_user)
        return response(data=_job_to_response(job))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/jobs", response_model=dict)
def list_jobs(
    current_user: User = Depends(get_current_user),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """GET /api/scheduler/jobs - Scheduled task list (T-511)"""
    jobs, total = service.get_jobs(current_user)
    return response(data={"items": [_job_to_response(j) for j in jobs], "total": total})


@router.get("/jobs/{job_id}", response_model=dict)
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """GET /api/scheduler/jobs/{id} - Get scheduled task (T-514)"""
    try:
        job = service.get_job(job_id, current_user)
        return response(data=_job_to_response(job))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.put("/jobs/{job_id}", response_model=dict)
def update_job(
    job_id: str,
    data: SchedulerJobUpdate,
    current_user: User = Depends(get_current_user),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """PUT /api/scheduler/jobs/{id} - Update scheduled task (T-515)"""
    try:
        job = service.update_job(job_id, data, current_user)
        return response(data=_job_to_response(job))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.delete("/jobs/{job_id}", response_model=dict)
def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """DELETE /api/scheduler/jobs/{id} - Delete scheduled task (T-512)"""
    try:
        service.delete_job(job_id, current_user)
        return response(message="Scheduled job deleted successfully")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/jobs/{job_id}/runs", response_model=dict)
def get_job_runs(
    job_id: str,
    current_user: User = Depends(get_current_user),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """GET /api/scheduler/jobs/{id}/runs - Execution records (T-513)"""
    try:
        runs, total = service.get_job_runs(job_id, current_user)
        return response(data={"items": runs, "total": total})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})
