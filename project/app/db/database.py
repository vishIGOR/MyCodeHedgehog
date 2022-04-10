import os
import asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "postgresql+asyncpg://petProjectsUser:password@127.0.0.1/myCodeHedgehogDB"
DB_NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
DB_KWARGS = {'echo': True}

engine = create_async_engine(DB_URL, **DB_KWARGS)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION, bind=engine)
Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    session = SessionLocal()
    async with session as db:
        yield db
