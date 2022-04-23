from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import authorize, authorize_only_admin, check_for_admin_role_or_id_by_token, GET_BEARER_SCHEME
from app.services.users import get_users_service, UsersService
from app.schemas.users import UserLogin, UserRegister, UserBaseData, UserDetailedData, UserPatchData
from app.schemas.tokens import AccessToken
from app.models.users import User
from app.db.database import get_db
from app.helpers.errors_helper import raise_if_http_error

router = APIRouter()


@router.get("/users", response_model=[], tags=["users"], description="Only for admin")
async def get_users(auth=Depends(authorize_only_admin), users_service: UsersService = Depends(get_users_service)):
    users = await users_service.get_users()

    raise_if_http_error(users)
    return users


@router.get("/users/{id}", response_model=UserDetailedData, tags=["users"],
            description="Only for admin or accaunt's owner")
async def get_user(id: int, token=Depends(GET_BEARER_SCHEME),
                   users_service: UsersService = Depends(get_users_service), db=Depends(get_db)):
    await check_for_admin_role_or_id_by_token(db, user_id=id, token=token)

    user = await users_service.get_user(id)
    raise_if_http_error(user)
    return user


@router.patch("/users/{id}", response_model=UserDetailedData, tags=["users"],
              description="Only for admin or accaunt's owner")
async def patch_user(id: int, user_dto: UserPatchData, token=Depends(GET_BEARER_SCHEME),
                     users_service: UsersService = Depends(get_users_service), db=Depends(get_db)):
    await check_for_admin_role_or_id_by_token(db, user_id=id, token=token)

    user = await users_service.change_user_data(id, user_dto)
    raise_if_http_error(user)
    return user


@router.delete("/users/{id}", tags=["users"], description="Only for admin or accaunt's owner")
async def delete_user(id: int, token=Depends(GET_BEARER_SCHEME),
                      users_service: UsersService = Depends(get_users_service), db=Depends(get_db)):
    await check_for_admin_role_or_id_by_token(db, user_id=id, token=token)

    raise_if_http_error(await users_service.delete_user(id))
    return status.HTTP_200_OK


@router.get("/users/{id}/profilePicture", response_class=FileResponse, tags=["users"],
            description="Only for admin or accaunt's owner")
async def get_avatar(id: int, token=Depends(GET_BEARER_SCHEME),
                     users_service: UsersService = Depends(get_users_service), db=Depends(get_db)):
    await check_for_admin_role_or_id_by_token(db, user_id=id, token=token)

    user_picture = await users_service.get_user_picture_path(id)
    raise_if_http_error(user_picture)
    return FileResponse(path=user_picture, filename="avatar.png",
                        media_type="image/png")


@router.post("/users/{id}/profilePicture", tags=["users"], description="Only for admin or accaunt's owner")
async def change_avatar(id: int, picture: UploadFile, token=Depends(GET_BEARER_SCHEME),
                        users_service: UsersService = Depends(get_users_service), db=Depends(get_db)):
    await check_for_admin_role_or_id_by_token(db, user_id=id, token=token)

    raise_if_http_error(await users_service.change_user_picture(id, picture))
    return status.HTTP_200_OK


@router.delete("/users/{id}/profilePicture", tags=["users"], description="Only for admin or accaunt's owner")
async def delete_avatar(id: int, token=Depends(GET_BEARER_SCHEME),
                        users_service: UsersService = Depends(get_users_service), db=Depends(get_db)):
    await check_for_admin_role_or_id_by_token(db, user_id=id, token=token)

    raise_if_http_error(await users_service.delete_user_picture(id))
    return status.HTTP_200_OK
