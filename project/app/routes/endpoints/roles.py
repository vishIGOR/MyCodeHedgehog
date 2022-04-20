from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.roles import RolesService, get_roles_service
from app.schemas.roles import RoleExtendedData
from app.models.roles import Role
from app.db.database import get_db
from app.helpers.errors_helper import raise_if_http_error

router = APIRouter()


@router.get("/roles", response_model=[], tags=["roles"])
async def get_roles(roles_service: RolesService = Depends(get_roles_service)):
    return await roles_service.get_roles()


@router.get("/roles/{id}", response_model=RoleExtendedData, tags=["roles"])
async def get_roles(id: int, roles_service: RolesService = Depends(get_roles_service)):
    result = await roles_service.get_role(id)

    raise_if_http_error(result)
    return result
