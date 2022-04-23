from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, exc
from fastapi import HTTPException, Header, Depends, status

from app.db.database import SessionLocal
from app.models.topics import Topic
from app.schemas.topics import *
from app.helpers.topics_helper import *
from app.helpers.errors_helper import is_http_error


class ITopicsService(ABC):
    @abstractmethod
    async def get_topics(self):
        pass

    @abstractmethod
    async def create_topic(self, topic_dto: TopicCreateData):
        pass

    @abstractmethod
    async def get_topic(self, topic_id: int):
        pass

    @abstractmethod
    async def change_topic_data(self, topic_id: int, topic_dto: TopicPatchData):
        pass

    @abstractmethod
    async def delete_topic(self, topic_id: int):
        pass

    @abstractmethod
    async def get_topic_childs(self, topic_id: int):
        pass

    @abstractmethod
    async def add_childs_to_topic(self, topic_id: int, childs: list[int]):
        pass

    @abstractmethod
    async def delete_topic_childs(self, topic_id: int, childs: list[int]):
        pass


class TopicsService(ITopicsService):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_topics(self):
        return await get_topics(self.db)

    async def create_topic(self, topic_dto: TopicCreateData):
        if (await is_topic_with_name_exists(self.db, topic_dto.name)):
            return HTTPException(status_code=400, detail="topic with this name is already exists")

        if not topic_dto.parent_id is None:
            if not (await is_topic_with_id_exists(self.db, topic_dto.parent_id)):
                return HTTPException(status_code=400, detail="parent topic with this id doesn't exist")

        new_topic = Topic(name=topic_dto.name,
                          description=topic_dto.description,
                          parent_id=topic_dto.parent_id
                          )

        try:
            self.db.add(new_topic)
            await self.db.commit()
        except:
            return HTTPException(status_code=500, detail="unexpected server error")

        await self.db.refresh(new_topic)
        return TopicData(id=new_topic.id, name=new_topic.name, description=new_topic.description,
                         parent_id=new_topic.parent_id)

    async def get_topic(self, topic_id: int):
        if not (await is_topic_with_id_exists(self.db, topic_id)):
            return HTTPException(status_code=400, detail="topic with this id doesn't exist")

        return await get_topic_with_childs_by_id(self.db, topic_id)

    async def change_topic_data(self, topic_id: int, topic_dto: TopicPatchData):
        topic = await get_topic_model_by_id(self.db, topic_id)
        if not topic:
            return HTTPException(status_code=400, detail="topic with this id doesn't exist")

        if not (topic_dto.name is None):
            if await is_topic_with_name_exists(self.db, topic_dto.name):
                if topic.name != topic_dto.name:
                    return HTTPException(status_code=400, detail="topic with this name already exists")

        if not (topic_dto.parent_id is None):
            if not (await is_topic_with_id_exists(self.db, topic_dto.parent_id)):
                return HTTPException(status_code=400, detail="parent topic with this id doesn't exist")

        result = await update_topic_using_patch_dto(self.db, topic_id, topic_dto)

        if is_http_error(result):
            return result

        return await get_topic_with_childs_by_id(self.db, topic_id)

    async def delete_topic(self, topic_id: int):
        if not (await is_topic_with_id_exists(self.db, topic_id)):
            return HTTPException(status_code=400, detail="topic with this id doesn't exist")

        return await delete_topic_by_id(self.db, topic_id)

    async def get_topic_childs(self, topic_id: int):
        if not (await is_topic_with_id_exists(self.db, topic_id)):
            return HTTPException(status_code=400, detail="topic with this id doesn't exist")

        return TopicChilds(childs=await get_topic_childs_by_id(self.db, topic_id))

    async def add_childs_to_topic(self, topic_id: int, childs: list[int]):
        if not (await is_topic_with_id_exists(self.db, topic_id)):
            return HTTPException(status_code=400, detail="topic with this id doesn't exist")

        for child in childs:
            if not (await  is_topic_with_id_exists(self.db, child)):
                return HTTPException(status_code=400, detail="at least one of the childs doesn't exist")
            if await is_topic_progenitor(self.db, child, topic_id):
                return HTTPException(status_code=400, detail="at least one of the childs is progenitor of this topic")

        for child in childs:
            response = await change_parent_of_topic(self.db, child, topic_id)
            if is_http_error(response):
                return response

        return await get_topic_with_childs_by_id(self.db, topic_id)

    async def delete_topic_childs(self, topic_id: int, childs: list[int]):
        if not (await is_topic_with_id_exists(self.db, topic_id)):
            return HTTPException(status_code=400, detail="topic with this id doesn't exist")

        if not (await is_array_are_childs_of_topic(self.db, topic_id, childs)):
            return HTTPException(status_code=400, detail="some topics are not childs")

        await delete_childs_of_topic(self.db, topic_id, childs)

        return await get_topic_with_childs_by_id(self.db, topic_id)


async def get_topics_service() -> ITopicsService:
    if not issubclass(TopicsService, ITopicsService):
        raise TypeError
    async with SessionLocal() as db:
        yield TopicsService(db)
