from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.roles import RolesService, get_roles_service
from app.schemas.roles import RoleExtendedData
from app.models.roles import Role
from app.db.database import get_db

router = APIRouter()


@router.get("/roles", response_model=[], tags=["roles"])
async def get_roles(roles_service: RolesService = Depends(get_roles_service)):
    return await roles_service.get_roles()


@router.get("/roles/{id}", response_model=RoleExtendedData, tags=["roles"])
async def get_roles(id: int, roles_service: RolesService = Depends(get_roles_service)):
    result = await roles_service.get_role(id)
    if result is None:
        raise HTTPException(400, detail="A role with this id doesn't exists")
    return result
