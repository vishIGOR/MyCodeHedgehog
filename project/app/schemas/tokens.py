from pydantic import BaseModel
from datetime import datetime


class AccessToken(BaseModel):
    access_token: str


class RefreshTokenScheme(BaseModel):
    refresh_token: str


class TokensPair(AccessToken, RefreshTokenScheme):
    pass
