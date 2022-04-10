from pydantic import BaseModel
from datetime import datetime


class RoleData(BaseModel):
    roleId: int


class RoleExtendedData(RoleData):
    name: str
