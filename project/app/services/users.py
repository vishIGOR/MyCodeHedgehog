from abc import ABC, abstractmethod
from shutil import copyfileobj
from os import path, stat

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status, UploadFile

from app.db.database import SessionLocal
from app.schemas.users import UserBaseData, UserRegister, UserDetailedData, UserPatchData
from app.helpers.users_helper import get_user_by_id, is_user_with_id_exists, update_user_using_patch_dto
from app.helpers.files_helper import is_file_image, save_file, is_file_size_more_that, is_file_exists, delete_file
from app.models.users import User
from app.models.roles import Role

PATH_TO_AVATARS = f"{path.dirname(path.dirname(path.abspath(__file__)))}/files/users_data/avatars"


class IUserService(ABC):
    @abstractmethod
    async def get_users(self):
        pass

    @abstractmethod
    async def get_user(self, user_id: int):
        pass

    @abstractmethod
    async def change_user_data(self, user_id: int, user_dto: UserPatchData):
        pass

    @abstractmethod
    async def delete_user(self, user_id: int):
        pass

    @abstractmethod
    async def get_user_picture_path(self, user_id: int):
        pass

    @abstractmethod
    async def change_user_picture(self, user_id: int, picture: UploadFile):
        pass

    @abstractmethod
    async def delete_user_picture(self, user_id: int):
        pass


class UsersService(IUserService):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self):
        user_models = await self.db.execute(select(User))

        user_dtos = []
        for user_model in user_models.scalars():
            user_dtos.append(
                UserBaseData(user_id=user_model.id, username=user_model.username, role_id=user_model.role_id))

        return user_dtos

    async def get_user(self, user_id: int):
        if not (await is_user_with_id_exists(self.db, user_id)):
            raise HTTPException(400, "user doesn't exist")

        user = await get_user_by_id(self.db, user_id)

        return UserDetailedData(
            user_id=user.id,
            username=user.username,
            role_id=user.role_id,
            name=user.name,
            surname=user.surname
        )

    async def change_user_data(self, user_id: int, user_dto: UserPatchData):
        await update_user_using_patch_dto(self.db, user_id, user_dto)

        return await self.get_user(user_id)

    async def delete_user(self, user_id: int):
        user = await get_user_by_id(self.db, user_id)
        if user is None:
            return None

        try:
            await self.db.delete(user)
            await self.db.commit()
        except exc:
            raise HTTPException(500, "unexpected server error")

    async def get_user_picture_path(self, user_id: int):
        picture_name = f"{user_id}.png"
        if is_file_exists(PATH_TO_AVATARS, picture_name):
            return PATH_TO_AVATARS + "/" + picture_name
        else:
            raise HTTPException(400, "avatar doesn't exists")

    async def change_user_picture(self, user_id: int, picture: UploadFile):
        if not is_file_image(picture):
            raise HTTPException(400, "Unsupported type of file")
        if is_file_size_more_that(picture, 250):
            raise HTTPException(400, "File is too big")

        print("test")
        save_file(picture, PATH_TO_AVATARS,
                  f"{user_id}.png")

    async def delete_user_picture(self, user_id: int):
        picture_name = f"{user_id}.png"
        if is_file_exists(PATH_TO_AVATARS, picture_name):
            delete_file(PATH_TO_AVATARS, picture_name)
        else:
            raise HTTPException(400, "avatar doesn't exists")


async def get_users_service() -> IUserService:
    if not issubclass(UsersService, IUserService):
        raise TypeError
    async with SessionLocal() as db:
        yield UsersService(db)
