from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import AuthService, get_auth_service, authorize, authorize_and_get_id, authorize_only_admin
from app.schemas.users import UserLogin, UserRegister, UserBaseData, UserDetailedData
from app.schemas.tokens import AccessToken
from app.models.users import User
from app.db.database import get_db

router = APIRouter()


@router.post("/auth/register", response_model=AccessToken)
async def register_user(user_dto: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.register_user(user_dto)

    return AccessToken(access_token=token)


@router.post("/auth/login", response_model=AccessToken)
async def login_user(user_dto: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.login_user(user_dto)

    return AccessToken(access_token=token)


@router.post("/auth/test")
async def test(test_var=Depends(authorize_only_admin)):
    return "hello"
