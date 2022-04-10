from fastapi import APIRouter

from app.routes.endpoints import roles


router = APIRouter()

router.include_router(roles.router)