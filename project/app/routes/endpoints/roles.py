from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import roles
from app.schemas.roles import RoleData, RoleExtendedData
from app.models.roles import Role
from app.db.database import get_db

router = APIRouter()


@router.get("/roles", response_model=[])
async def get_roles(db: AsyncSession = Depends(get_db)):
    return await roles.get_roles(db)


@router.get("/roles/{id}", response_model=[])
async def get_roles(id: int, db: AsyncSession = Depends(get_db)):
    result = await roles.get_role(db, id)
    if result is None:
        raise HTTPException(400,detail="A role with this id doesn't exists")
    return result
