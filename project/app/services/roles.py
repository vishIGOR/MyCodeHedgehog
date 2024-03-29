from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status

from app.db.database import SessionLocal
from app.models.roles import Role
from app.schemas.roles import RoleData, RoleExtendedData


async def get_roles_service():
    async with SessionLocal() as db:
        async with db.begin():
            yield RolesService(db)


class IRolesService(ABC):
    @abstractmethod
    async def get_roles(self):
        pass

    @abstractmethod
    async def get_role(self, role_id: int):
        pass


class RolesService(IRolesService):
    def __init__(self, db: SessionLocal):
        self.db = db

    async def get_roles(self):
        role_models = await self.db.execute(select(Role))

        extended_roles = []
        for role_model in role_models.scalars():
            extended_roles.append(RoleExtendedData(roleId=role_model.id, name=role_model.name))

        return extended_roles

    async def get_role(self, role_id: int):
        try:
            role_model = (await self.db.execute(select(Role).where(Role.id == role_id))).scalars().one()
        except exc.NoResultFound:
            return HTTPException(400, detail="A role with this id doesn't exists")

        return RoleExtendedData(roleId=role_model.id, name=role_model.name)


async def get_roles_service() -> IRolesService:
    if not issubclass(RolesService, IRolesService):
        raise TypeError
    async with SessionLocal() as db:
        async with db.begin():
            yield RolesService(db)
