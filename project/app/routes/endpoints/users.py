from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import AuthService, get_auth_service, authorize
from app.schemas.users import UserLogin, UserRegister, UserBaseData, UserDetailedData
from app.schemas.tokens import AccessToken
from app.models.users import User
from app.db.database import get_db

router = APIRouter()


@router.get("/users", response_model=[])
async def get_users(user_dto: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.register_user(user_dto)

    return AccessToken(access_token=token)


