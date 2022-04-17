from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import authorize, authorize_only_admin, authorize_and_get_id, oauth2_scheme
from app.services.users import get_users_service, UsersService
from app.schemas.users import UserLogin, UserRegister, UserBaseData, UserDetailedData
from app.schemas.tokens import AccessToken
from app.models.users import User
from app.db.database import get_db

router = APIRouter()


@router.get("/users", response_model=[], tags=["users"])
async def get_users(auth=Depends(authorize_only_admin), users_service: UsersService = Depends(get_users_service)):
    return await users_service.get_users()


@router.get("/users/{id}", response_model=[], tags=["users"])
async def get_users(id: int, id_from_token=Depends(authorize_and_get_id),
                    users_service: UsersService = Depends(get_users_service)):
    if id != id_from_token:
        await authorize_only_admin(db=Depends(get_db), token=Depends(oauth2_scheme))

    return await users_service.get_user(id)

