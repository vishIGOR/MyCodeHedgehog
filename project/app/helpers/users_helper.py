from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, exc
from fastapi import HTTPException

from app.models.users import User
from app.schemas.users import UserPatchData
from app.helpers.hash_helper import hash_password


async def get_role_name_by_user_id(db: AsyncSession, user_id: int):
    try:
        user = (
            await db.execute(select(User).where(User.id == user_id).options(selectinload(User.role)))).scalars().one()
    except exc.NoResultFound:
        return None
    if user.role is None:
        return None

    return user.role.name


async def get_user_id_by_username(db: AsyncSession, username: str):
    user = await get_user_by_username(db, username)

    if user is None:
        return None

    return user.id


async def is_user_with_username_exists(db: AsyncSession, username: str):
    try:
        user = (await db.execute(select(User).where(User.username == username))).scalars().one()
    except exc.NoResultFound:
        return False

    return True


async def is_user_with_id_exists(db: AsyncSession, user_id: int):
    try:
        user = (await db.execute(select(User).where(User.id == user_id))).scalars().one()
    except exc.NoResultFound:
        return False

    return True


async def get_user_by_username(db: AsyncSession, username: str):
    try:
        user = (await db.execute(select(User).where(User.username == username))).scalars().one()
    except exc.NoResultFound:
        return None

    return user


async def get_user_by_id(db: AsyncSession, user_id: id):
    try:
        user = (await db.execute(select(User).where(User.id == user_id))).scalars().one()
    except exc.NoResultFound:
        return None

    return user


async def update_user_using_patch_dto(db: AsyncSession, user_id: int, user_dto: UserPatchData):
    user_old_dto = await  get_user_patch_dto_by_id(db, user_id)
    update_data = user_dto.dict(exclude_unset=True)
    if "password" in update_data.keys():
        update_data["password"] = hash_password(update_data["password"])
    new_dto = user_old_dto.copy(update=update_data)

    try:
        q = update(User).where(User.id == user_id)
        q = q.values(name=new_dto.name)
        q = q.values(surname=new_dto.surname)
        q = q.values(password=new_dto.password)
        await (db.execute(q))
        await db.commit()
    except exc as e:
        raise HTTPException(400, "some data is strange")


async def get_user_patch_dto_by_id(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    if user is None:
        return None

    return UserPatchData(name=user.name, surname=user.surname, password=user.password)
