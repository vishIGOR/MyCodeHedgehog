from random import choice
from string import ascii_letters
from hashlib import pbkdf2_hmac
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.db.database import get_db, SessionLocal
from app.models.users import User
from app.schemas.users import UserLogin, UserRegister, UserDetailedData, UserBaseData
from app.schemas.tokens import AccessToken

SECRET_KEY = "3fdf5df59d68c1b67a4a241d51e3f7b119df9ada0706342ff77825154897b1b8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7
STRING_DATE_FORMAT = "%b %d %Y %H %M %S %f"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="unauthorized",
    headers={"WWW-Authenticate": "Bearer"}
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_auth_service():
    async with SessionLocal() as db:
        yield AuthService(db)


class AuthService():
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

        return await create_user_token(self.db, user_dto.username)

    async def login_user(self, user_dto: UserLogin):
        user_model = await get_user_by_username(self.db, user_dto.username)

        if user_model is None:
            raise HTTPException(status_code=400, detail="incorrect login or password")

        if not validate_password(user_dto.password, user_model.password):
            raise HTTPException(status_code=400, detail="incorrect login or password")

        return await create_user_token(self.db, user_dto.username)


async def authorize(db: AsyncSession = Depends(get_db), token=Depends(oauth2_scheme)):
    if not (await is_token_valid(db, token)):
        raise unauthorized_exception


async def authorize_and_get_id(db: AsyncSession = Depends(get_db), token=Depends(oauth2_scheme)):
    await authorize(db, token)

    return await get_user_id_from_token(db, token)


async def authorize_only_admin(db: AsyncSession = Depends(get_db), token=Depends(oauth2_scheme)):
    await authorize(db, token)

    if (not (await get_role_name_from_token(db, token)) == "admin"):
        raise unauthorized_exception


async def is_token_valid(db: AsyncSession, token: str) -> bool:
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


async def get_role_name_from_token(db: AsyncSession, token: str):
    return await get_role_name_by_user_id(db, await get_user_id_from_token(db, token))


async def get_user_id_from_token(db: AsyncSession, token: str):
    decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = decoded_jwt.get("user_id")

    return user_id


async def create_user_token(db: AsyncSession, username: str):
    user_id = await get_user_id_by_username(db, username)
    if user_id is None:
        return None

    to_encode = {"user_id": user_id}
    expire = datetime.strftime(datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS), STRING_DATE_FORMAT)
    to_encode.update({"expires": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # TODO: создание refresh токена с помощью redis

    return encoded_jwt


async def get_role_name_by_user_id(db: AsyncSession, user_id: int):
    try:
        user = (await db.execute(select(User).where(User.id == user_id).options(selectinload(User.role)))).scalars().one()
    except exc.NoResultFound:
        return None
    if user is None:
        return None
    if user.role is None:
        return None

    return user.role.name


async def get_user_id_by_username(db: AsyncSession, username: str):
    user = await get_user_by_username(db, username)

    if user is None:
        return None

    return user.id


async def get_user_by_username(db: AsyncSession, username: str):
    try:
        user = (await db.execute(select(User).where(User.username == username))).scalars().one()
    except exc.NoResultFound:
        return None

    return user


async def get_user_by_id(db: AsyncSession, user_id: id):
    try:
        user = (await db.execute(select(User).where(User.id == user_id))).scalars().one()
    except exc.NoResultFound:
        return None

    return user


async def is_user_with_username_exists(db: AsyncSession, username: str):
    try:
        user = (await db.execute(select(User).where(User.username == username))).scalars().one()
    except exc.NoResultFound:
        return False

    return True


async def is_user_with_id_exists(db: AsyncSession, user_id: int):
    try:
        user = (await db.execute(select(User).where(User.id == user_id))).scalars().one()
    except exc.NoResultFound:
        return False

    return True


def get_random_string(length: int = 12):
    return "".join(choice(ascii_letters) for _ in range(length))


def hash_password(password: str):
    return pwd_context.hash(password)


def validate_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)
