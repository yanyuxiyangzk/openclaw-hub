from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db, SessionLocal
from core.security import get_current_user
from core.exceptions import AppException, NotFoundException, ForbiddenException, BadRequestException
from models.user import User
from schemas.execution import (
    ExecutionCreate, ExecutionResponse, ExecutionListResponse, ExecutionOutputResponse
)
from schemas.task import TaskCreate
from services.execution_service import ExecutionService
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["executions"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_execution_service(db: Session = Depends(get_db)) -> ExecutionService:
    return ExecutionService(db)


def _process_execution_background(execution_id: str):
    """Background task to process a single execution."""
    db = SessionLocal()
    try:
        execution_service = ExecutionService(db)
        execution_service.start_execution(execution_id)
        execution_service.complete_execution(
            execution_id,
            output_data={"status": "completed", "message": "Execution processed"},
        )
    except Exception as e:
        try:
            execution_service.complete_execution(
                execution_id,
                error_message=str(e),
            )
        except Exception:
            pass
    finally:
        db.close()


class BatchExecuteRequest(BaseModel):
    task_ids: list[str]
    agent_id: str


def _execution_to_response(execution) -> dict:
    import json
    input_data = execution.input_data
    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except:
            input_data = None

    output_data = execution.output_data
    if isinstance(output_data, str):
        try:
            output_data = json.loads(output_data)
        except:
            output_data = None

    return {
        "id": execution.id,
        "task_id": execution.task_id,
        "agent_id": execution.agent_id,
        "status": execution.status,
        "input_data": input_data,
        "output_data": output_data,
        "error_message": execution.error_message,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "created_at": execution.created_at,
    }


@router.post("/tasks/{task_id}/execute", response_model=dict)
def trigger_execution(
    task_id: str,
    data: ExecutionCreate,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """POST /api/tasks/{id}/execute - Trigger task execution (T-501)"""
    try:
        data.task_id = task_id
        execution = service.create_execution(data, current_user)
        return response(data=_execution_to_response(execution))
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/tasks/{task_id}/execute/batch", response_model=dict)
def batch_execute(
    task_id: str,
    data: BatchExecuteRequest,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """POST /api/tasks/{id}/execute/batch - Batch execution (T-502)"""
    try:
        task_ids = [task_id] + data.task_ids
        executions = service.batch_execute(task_ids, data.agent_id, current_user)
        return response(data={"items": [_execution_to_response(e) for e in executions], "total": len(executions)})
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/executions", response_model=dict)
def list_executions(
    status: str = Query(None, description="Filter by status: pending, running, completed, failed, cancelled"),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """GET /api/executions - List all executions with optional status filter (T-530)"""
    try:
        executions, total = service.list_executions(status, current_user)
        return response(data={"items": [_execution_to_response(e) for e in executions], "total": total})
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/executions/active", response_model=dict)
def get_active_executions(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """GET /api/executions/active - Current active executions (T-508)"""
    try:
        executions, total = service.get_active_executions(current_user)
        return response(data={"items": [_execution_to_response(e) for e in executions], "total": total})
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/executions/{execution_id}", response_model=dict)
def get_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """GET /api/executions/{id} - Execution record detail (T-503)"""
    try:
        execution = service.get_execution(execution_id, current_user)
        return response(data=_execution_to_response(execution))
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/tasks/{task_id}/executions", response_model=dict)
def get_task_executions(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """GET /api/tasks/{id}/executions - Task execution history (T-504)"""
    try:
        executions, total = service.get_task_executions(task_id, current_user)
        return response(data={"items": [_execution_to_response(e) for e in executions], "total": total})
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/executions/{execution_id}/cancel", response_model=dict)
def cancel_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """POST /api/executions/{id}/cancel - Cancel execution (T-505)"""
    try:
        execution = service.cancel_execution(execution_id, current_user)
        return response(data=_execution_to_response(execution))
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.post("/executions/{execution_id}/retry", response_model=dict)
def retry_execution(
    execution_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """POST /api/executions/{id}/retry - Retry execution (T-506)"""
    try:
        execution = service.retry_execution(execution_id, current_user)
        background_tasks.add_task(_process_execution_background, execution.id)
        return response(data=_execution_to_response(execution))
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/executions/{execution_id}/output", response_model=dict)
def get_execution_output(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """GET /api/executions/{id}/output - Execution output (T-507)"""
    try:
        result = service.get_execution_output(execution_id, current_user)
        return response(data=result)
    except AppException:
        raise
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})