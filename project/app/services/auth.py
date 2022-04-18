from hashlib import pbkdf2_hmac
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.db.database import get_db, SessionLocal
from app.models.users import User
from app.models.tokens import RefreshToken
from app.schemas.users import UserLogin, UserRegister, UserDetailedData, UserBaseData
from app.schemas.tokens import AccessToken, RefreshTokenScheme, TokensPair
from app.helpers.users_helper import *
from app.helpers.hash_helper import generate_token, hash_password, validate_password

SECRET_KEY = "3fdf5df59d68c1b67a4a241d51e3f7b119df9ada0706342ff77825154897b1b8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 3
STRING_DATE_FORMAT = "%b %d %Y %H %M %S %f"

UNAUTHORIZED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="unauthorized",
    headers={"WWW-Authenticate": "Bearer"}
)
GET_BEARER_SCHEME = OAuth2PasswordBearer(tokenUrl="token")


class IAuthService(ABC):
    @abstractmethod
    async def register_user(self, user_dto: UserRegister):
        pass

    @abstractmethod
    async def login_user(self, user_dto: UserLogin):
        pass

    @abstractmethod
    async def re_auth(self, token: RefreshTokenScheme):
        pass


class AuthService(IAuthService):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_dto: UserRegister):
        if (await is_user_with_username_exists(self.db, user_dto.username)):
            raise HTTPException(status_code=400, detail="user with this username is already exists")

        new_user = User(username=user_dto.username,
                        name=user_dto.name,
                        surname=user_dto.surname,
                        password=hash_password(user_dto.password)
                        )

        try:
            self.db.add(new_user)
            await self.db.commit()
        except:
            raise HTTPException(status_code=500, detail="unexpected server error")

        self.db.refresh(new_user)
        return await create_tokens_pair(self.db, new_user.id)

    async def login_user(self, user_dto: UserLogin):
        user_model = await get_user_by_username(self.db, user_dto.username)

        if user_model is None:
            raise HTTPException(status_code=400, detail="incorrect login or password")

        if not validate_password(user_dto.password, user_model.password):
            raise HTTPException(status_code=400, detail="incorrect login or password")

        user_id = user_model.id
        return await create_tokens_pair(self.db, user_id)

    async def re_auth(self, token: RefreshTokenScheme):
        refresh_token_model = await get_refresh_token_by_string(self.db, token.refresh_token)
        if refresh_token_model is None:
            raise UNAUTHORIZED_EXCEPTION

        return await create_tokens_pair(self.db, refresh_token_model.user_id)


async def get_auth_service() -> IAuthService:
    if not issubclass(AuthService, IAuthService):
        raise TypeError
    async with SessionLocal() as db:
        yield AuthService(db)


async def authorize_and_get_id(db: AsyncSession = Depends(get_db), token=Depends(GET_BEARER_SCHEME)):
    await authorize(db, token)

    return await get_user_id_from_access_token(db, token)


async def authorize_only_admin(db: AsyncSession = Depends(get_db), token=Depends(GET_BEARER_SCHEME)):
    await authorize(db, token)

    if not (await is_user_admin_by_token(db, token)):
        raise UNAUTHORIZED_EXCEPTION


async def authorize(db: AsyncSession = Depends(get_db), token=Depends(GET_BEARER_SCHEME)):
    if not (await is_access_token_valid(db, token)):
        raise UNAUTHORIZED_EXCEPTION


async def check_for_admin_role_or_id_by_token(db: AsyncSession, user_id: int, token: str) -> bool:
    id_from_token = await authorize_and_get_id(db, token)
    if user_id != id_from_token:
        if not (await is_access_token_valid(db, token)):
            raise UNAUTHORIZED_EXCEPTION


async def create_tokens_pair(db: AsyncSession, user_id: int):
    to_encode = {"user_id": user_id}
    expire = datetime.strftime(datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), STRING_DATE_FORMAT)
    to_encode.update({"expires": expire})
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    generated_token = generate_token()
    new_refresh_token = RefreshToken(
        token=generated_token,
        user_id=user_id
    )

    try:
        old_refresh_token = (
            await db.execute(select(RefreshToken).where(RefreshToken.user_id == user_id))).scalars().one()
        await db.delete(old_refresh_token)
        await db.commit()
    except:
        pass

    try:
        db.add(new_refresh_token)
        await db.commit()
    except:
        raise HTTPException(status_code=500, detail="unexpected server error")

    return TokensPair(access_token=access_token, refresh_token=generated_token)


async def is_access_token_valid(db: AsyncSession, token: str) -> bool:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded_jwt.get("user_id")
        expires: datetime = datetime.strptime(decoded_jwt.get("expires"), STRING_DATE_FORMAT)
    except:
        return False

    if user_id is None:
        return False
    if (await is_user_with_id_exists(db, user_id)) is None:
        return False

    if datetime is None:
        return False
    if datetime.utcnow() > expires:
        return False

    return True


async def get_refresh_token_by_string(db: AsyncSession, string: str):
    '''returns RefreshToken (db model) by token(string)'''
    try:
        token = (await db.execute(select(RefreshToken).where(RefreshToken.token == string))).scalars().one()
    except exc.NoResultFound:
        return None

    return token


async def is_user_admin_by_token(db: AsyncSession, token: str):
    role = await  get_role_name_by_user_id(db, await get_user_id_from_access_token(db, token))
    if role == "admin":
        return True

    return False


async def get_user_id_from_access_token(db: AsyncSession, token: str):
    decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = decoded_jwt.get("user_id")

    return user_id
