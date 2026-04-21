from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.orgs import router as orgs_router
from routers.invitations import router as invitations_router
from routers.projects import router as projects_router
from routers.agents import router as agents_router
from routers.ws import router as ws_router
from routers.phase3 import router as phase3_router
from routers.tasks import router as tasks_router

__all__ = ["auth_router", "users_router", "orgs_router", "invitations_router", "projects_router", "agents_router", "ws_router", "phase3_router", "tasks_router"]
