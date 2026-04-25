from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db, SessionLocal
from core.security import get_current_user
from models.user import User
from schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowExecuteRequest
)
from services.workflow_service import WorkflowService
from services.execution_service import ExecutionService
import json

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


def get_workflow_service(db: Session = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)


def _workflow_to_response(workflow) -> dict:
    steps = workflow.steps
    if isinstance(steps, str):
        try:
            steps = json.loads(steps)
        except:
            steps = []

    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "steps": steps,
        "org_id": workflow.org_id,
        "created_by": workflow.created_by,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
    }


def _execution_to_response(execution) -> dict:
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


@router.post("", response_model=dict)
def create_workflow(
    data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """POST /api/workflows - Create workflow (T-520)"""
    try:
        workflow = service.create_workflow(data, current_user)
        return response(data=_workflow_to_response(workflow))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("/{workflow_id}", response_model=dict)
def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """GET /api/workflows/{id} - Workflow detail (T-521)"""
    try:
        workflow = service.get_workflow(workflow_id, current_user)
        return response(data=_workflow_to_response(workflow))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


def _process_execution_background(execution_id: str):
    """Background task to process a single execution."""
    db = SessionLocal()
    try:
        execution_service = ExecutionService(db)
        execution_service.start_execution(execution_id)
        # In production, this would call the agent runtime API
        # For now, simulate completion with a placeholder result
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


@router.post("/{workflow_id}/execute", response_model=dict)
def execute_workflow(
    workflow_id: str,
    data: WorkflowExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """POST /api/workflows/{id}/execute - Execute workflow (T-522)"""
    try:
        executions = service.execute_workflow(workflow_id, data, current_user)
        # Register background tasks to process each execution
        for execution in executions:
            background_tasks.add_task(_process_execution_background, execution.id)
        return response(data={"items": [_execution_to_response(e) for e in executions], "total": len(executions)})
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.get("", response_model=dict)
def list_workflows(
    org_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """GET /api/workflows - List workflows"""
    workflows, total = service.get_workflows(org_id, current_user)
    return response(data={"items": [_workflow_to_response(w) for w in workflows], "total": total})


@router.put("/{workflow_id}", response_model=dict)
def update_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """PUT /api/workflows/{id} - Update workflow"""
    try:
        workflow = service.update_workflow(workflow_id, data, current_user)
        return response(data=_workflow_to_response(workflow))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})


@router.delete("/{workflow_id}", response_model=dict)
def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """DELETE /api/workflows/{id} - Delete workflow"""
    try:
        service.delete_workflow(workflow_id, current_user)
        return response(message="Workflow deleted successfully")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": 40301, "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": 40401, "message": str(e)})
