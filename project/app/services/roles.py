from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status

from app.models.roles import Role
from app.schemas.roles import RoleData, RoleExtendedData


async def get_roles(db: AsyncSession):
    role_models = await db.execute(select(Role))

    extended_roles = []
    for role_model in role_models.scalars():
        extended_roles.append(RoleExtendedData(roleId=role_model.id, name=role_model.name))

    return extended_roles


async def get_role(db: AsyncSession, roleId: int):
    try:
        role_model = (await db.execute(select(Role).where(Role.id == roleId))).scalars().one()
    except exc.NoResultFound:
        return None

    return RoleExtendedData(roleId=role_model.id, name=role_model.name)
