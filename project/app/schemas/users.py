from typing import Optional
from pydantic import BaseModel, constr


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: constr(min_length=1, max_length=30)
    password: constr(min_length=8, max_length=50)
    name: constr(min_length=1, max_length=50)
    surname: constr(min_length=1, max_length=50)


class UserPatchData(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    surname: Optional[constr(min_length=1, max_length=50)] = None
    password: Optional[constr(min_length=8, max_length=50)] = None


class UserBaseData(BaseModel):
    user_id: int
    username: str
    role_id: Optional[int] = None


class UserDetailedData(UserBaseData):
    name: str
    surname: str
