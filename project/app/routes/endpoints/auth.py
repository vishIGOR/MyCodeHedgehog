from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import AuthService, get_auth_service, authorize, authorize_and_get_id, authorize_only_admin
from app.schemas.users import UserLogin, UserRegister, UserBaseData, UserDetailedData
from app.schemas.tokens import AccessToken,TokensPair
from app.models.users import User
from app.db.database import get_db

router = APIRouter()


@router.post("/auth/register", response_model=TokensPair, tags=["auth"])
async def register_user(user_dto: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    tokens_pair = await auth_service.register_user(user_dto)

    return tokens_pair


@router.post("/auth/login", response_model=TokensPair, tags=["auth"])
async def login_user(user_dto: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    tokens_pair = await auth_service.login_user(user_dto)

    return tokens_pair


@router.post("/auth/reauth", response_model=TokensPair, tags=["auth"])
async def login_user(tokens: TokensPair, auth_service: AuthService = Depends(get_auth_service)):
    tokens_pair = await auth_service.re_auth(tokens)

    return tokens_pair

@router.post("/auth/test", tags=["auth"])
async def test(refreshToken = Header(None,alias="refresh_token")):
    return refreshToken
