from os import path
from inspect import stack

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from alembic.config import Config
from alembic import command
from loguru import logger

from app import models
from app.db.database import engine, get_db, Base, metadata
from app.routes.router import router

app = FastAPI()


app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.add("app\logs.log", format= "{time} {message}", rotation = "100 KB")
    await start_db()


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
