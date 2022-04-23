from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, exc
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.models.topics import Topic
from app.schemas.topics import TopicCreateData, TopicData, TopicDataWithChilds, TopicPatchData


async def update_topic_using_patch_dto(db: AsyncSession, topic_id: int, topic_dto: TopicPatchData):
    topic_old_dto = await get_topic_patch_dto_by_id(db, topic_id)
    update_data = topic_dto.dict(exclude_unset=True)

    new_dto = topic_old_dto.copy(update=update_data)

    try:
        q = update(Topic).where(Topic.id == topic_id)
        q = q.values(name=new_dto.name)
        q = q.values(description=new_dto.description)
        q = q.values(parent_id=new_dto.parent_id)
        await db.execute(q)
        await db.commit()
    except SQLAlchemyError:
        return HTTPException(500, "smth gone wrong")


async def get_topic_patch_dto_by_id(db: AsyncSession, topic_id: int):
    topic = await get_topic_model_by_id(db, topic_id)

    return TopicPatchData(name=topic.name, description=topic.description, parent_id=topic.parent_id)


async def change_parent_of_topic(db: AsyncSession, topic_id: int, new_parent_id: int):
    try:
        q = update(Topic).where(Topic.id == topic_id)
        q = q.values(parent_id=new_parent_id)
        await (db.execute(q))
        await db.commit()
    except SQLAlchemyError:
        return HTTPException(500, "smth gone wrong")


async def delete_childs_of_topic(db: AsyncSession, topic_id: int, childs: list[int]):
    for child_id in childs:
        await delete_topic_by_id(db, child_id)


async def is_array_are_childs_of_topic(db: AsyncSession, topic_id: int, childs: list[int]):
    for child_id in childs:
        if not (await is_topic_with_id_exists(db, child_id)):
            return False
        if not (await is_topic_direct_parent(db, topic_id, child_id)):
            return False

    return True


async def is_topic_progenitor(db: AsyncSession, topic_id: int, possible_child_id: int):
    topic = await get_topic_model_by_id(db, possible_child_id)

    low_topic_id = possible_child_id
    high_topic_id = topic.parent_id

    while not high_topic_id is None:
        if high_topic_id == topic_id:
            return True
        high_topic = await get_topic_model_by_id(db, high_topic_id)
        if high_topic_id is None:
            return False

        low_topic_id = high_topic_id
        high_topic_id = high_topic.parent_id

    return False


async def is_topic_direct_parent(db: AsyncSession, topic_id: int, possible_child_id: int):
    topic = await get_topic_model_by_id(db, possible_child_id)

    if topic.parent_id is None:
        return False
    if topic.parent_id != topic_id:
        return False

    return True


async def delete_topic_by_id(db: AsyncSession, topic_id: int):
    topic = await get_topic_model_by_id(db, topic_id)

    try:
        await db.delete(topic)
        await db.commit()
    except:
        return HTTPException(500, "unexpected server error")


async def get_topic_with_childs_by_id(db: AsyncSession, topic_id: int):
    topic = await get_topic_model_by_id(db, topic_id)
    childs = await get_topic_childs_by_id(db, topic_id)

    return TopicDataWithChilds(id=topic.id,
                               name=topic.name,
                               description=topic.description,
                               parent_id=topic.parent_id,
                               childs=childs)


async def get_topic_childs_by_id(db: AsyncSession, topic_id: int):
    topic_models = await db.execute(select(Topic).where(Topic.parent_id == topic_id))

    topic_dtos = []
    for topic_model in topic_models.scalars():
        topic_dtos.append(TopicData(id=topic_model.id,
                                    name=topic_model.name,
                                    description=topic_model.description,
                                    parent_id=topic_model.parent_id
                                    ))

    return topic_dtos


async def get_topics(db: AsyncSession):
    topic_models = await db.execute(select(Topic))

    topic_dtos = []
    for topic_model in topic_models.scalars():
        topic_dtos.append(TopicData(id=topic_model.id,
                                    name=topic_model.name,
                                    description=topic_model.description,
                                    parent_id=topic_model.parent_id
                                    ))

    return topic_dtos


async def is_topic_with_name_exists(db: AsyncSession, topic_name: str):
    if (await get_topic_model_by_name(db, topic_name)) is None:
        return False

    return True


async def is_topic_with_id_exists(db: AsyncSession, topic_id: int):
    if (await get_topic_model_by_id(db, topic_id)) is None:
        return False

    return True


async def get_topic_model_by_name(db: AsyncSession, topic_name: str):
    try:
        topic = (await db.execute(
            select(Topic).where(Topic.name == topic_name).options(selectinload(Topic.parent)))).scalars().one()
    except exc.NoResultFound:
        return None

    return topic


async def get_topic_model_by_id(db: AsyncSession, topic_id: int):
    try:
        topic = (await db.execute(
            select(Topic).where(Topic.id == topic_id).options(selectinload(Topic.parent)))).scalars().one()
    except exc.NoResultFound:
        return None

    return topic
