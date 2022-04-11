from typing import Optional
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(UserLogin):
    name: str
    surname: str


class UserBaseData(BaseModel):
    user_id: int
    username: str
    role_id: Optional[int] = None


class UserDetailedData(UserBaseData):
    name: str
    surname: str
