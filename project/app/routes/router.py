from fastapi import APIRouter

from app.routes.endpoints import roles, auth, users, topics

router = APIRouter()

router.include_router(auth.router)
router.include_router(roles.router)
router.include_router(users.router)
router.include_router(topics.router)
