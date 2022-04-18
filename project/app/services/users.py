from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status

from app.db.database import SessionLocal
from app.schemas.users import UserBaseData, UserRegister, UserDetailedData, UserPatchData
from app.helpers.users_helper import get_user_by_id, is_user_with_id_exists, update_user_using_patch_dto
from app.models.users import User
from app.models.roles import Role


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


async def get_users_service() -> IUserService:
    if not issubclass(UsersService, IUserService):
        raise TypeError
    async with SessionLocal() as db:
        yield UsersService(db)
