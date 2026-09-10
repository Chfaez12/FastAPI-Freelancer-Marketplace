from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.skills import router as skills_router
from app.routers.profiles import router as profiles_router
from app.routers.jobs import router as jobs_router
from app.routers.proposals import router as proposals_router
from app.routers.contracts import router as contracts_router
from app.routers.milestones import router as milestones_router
from app.routers.reviews import router as reviews_router

__all__ = [
    "auth_router",
    "users_router",
    "skills_router",
    "profiles_router",
    "jobs_router",
    "proposals_router",
    "contracts_router",
    "milestones_router",
    "reviews_router",
]