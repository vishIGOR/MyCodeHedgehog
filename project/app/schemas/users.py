from typing import Optional
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(UserLogin):
    name: str
    surname: str


class UserBaseData(BaseModel):
    userId: int
    username: str
    roleId: Optional[int] = None


class UserDetailedData(UserBaseData):
    name: str
    surname: str
