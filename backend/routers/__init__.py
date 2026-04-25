from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.orgs import router as orgs_router
from routers.invitations import router as invitations_router
from routers.projects import router as projects_router
from routers.agents import router as agents_router
from routers.agent_roles import router as agent_roles_router
from routers.ws import router as ws_router
from routers.phase3 import router as phase3_router
from routers.tasks import router as tasks_router
from routers.executions import router as executions_router
from routers.scheduler import router as scheduler_router
from routers.workflows import router as workflows_router
from routers.activities import router as activities_router
from routers.dashboard import router as dashboard_router

__all__ = ["auth_router", "users_router", "orgs_router", "invitations_router", "projects_router", "agents_router", "agent_roles_router", "ws_router", "phase3_router", "tasks_router", "executions_router", "scheduler_router", "workflows_router", "activities_router", "dashboard_router"]
