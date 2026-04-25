from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles
import os
from config import get_settings
from routers import auth_router, users_router, orgs_router, invitations_router, projects_router, agents_router, agent_roles_router, ws_router, phase3_router, tasks_router, executions_router, scheduler_router, workflows_router, activities_router, dashboard_router
from core.database import engine, Base
from core.exceptions import AppException, ErrorCodes
import logging
import traceback

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "openclawhub"}


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    from core.database import engine
    from sqlalchemy import text
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "healthy",
        "service": "openclawhub-api",
        "database": db_status
    }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": detail["code"], "message": detail.get("message", "Error"), "data": None}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code * 100, "message": str(detail) if detail else "Error", "data": None}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"code": 42201, "message": "Validation error", "data": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions - returns standardized 500 error"""
    logger.error(f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}")
    logger.error(traceback.format_exc())

    # If it's already an AppException (or HTTPException), let FastAPI handle it
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": exc.details
            }
        )

    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code * 100,
                "message": str(exc.detail) if hasattr(exc, 'detail') else "Error",
                "data": None
            }
        )

    # Generic 500 error
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCodes.INTERNAL_ERROR,
            "message": "Internal server error",
            "data": None
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orgs_router)
app.include_router(invitations_router)
app.include_router(projects_router)
app.include_router(agents_router)
app.include_router(agent_roles_router)
app.include_router(ws_router)
app.include_router(phase3_router)
app.include_router(tasks_router)
app.include_router(executions_router)
app.include_router(scheduler_router)
app.include_router(workflows_router)
app.include_router(activities_router)
app.include_router(dashboard_router)

# Serve uploaded files
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {"message": "OpenClawHub API", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
