import os
import asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.db.settings import *

engine = create_async_engine(DB_URL, **DB_KWARGS)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION, bind=engine)
Base = declarative_base(metadata=metadata)


async def get_db() -> SessionLocal:
    session = SessionLocal()
    async with session as db:
        try:
            yield db
        finally:
            db.close()
