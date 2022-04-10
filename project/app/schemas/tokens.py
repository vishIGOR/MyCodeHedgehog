from pydantic import BaseModel
from datetime import datetime


class AccessToken(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokensPair(AccessToken, RefreshToken):
    pass
