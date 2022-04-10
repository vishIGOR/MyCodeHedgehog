from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status

from app.schemas.users import UserBaseData, UserRegister
from app.models.users import User
from app.models.roles import Role



# class UsersService():
#     def __init__(self, db:AsyncSession):
#         self.db = db
#
#     async def get_users(self):
