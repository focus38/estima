from fastapi import APIRouter

from backend import config

role_router = APIRouter()

@role_router.get("/api/roles")
async def get_roles():
    return {
        "roles": config.DEFAULT_ROLES
    }