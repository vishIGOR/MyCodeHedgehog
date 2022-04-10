from os import path
from inspect import stack

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from alembic.config import Config
from alembic import command

from app import models
from app.db.database import engine, get_db, Base, metadata
from app.routes.router import router

app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await start_db()
    # try:
    #     await run_async_upgrade()
    # except Exception as e:
    #     print(str(e))


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# def run_upgrade(connection, cfg):
#     cfg.attributes['connection']=connection
#     command.upgrade(cfg, "head")
#
# async def run_async_upgrade():
#     async with engine.begin() as conn:
#         await conn.run_sync(run_upgrade, Config(path.dirname(path.dirname(path.dirname(__file__))) + "\\alembic.ini"))
