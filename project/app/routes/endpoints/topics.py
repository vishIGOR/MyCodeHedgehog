from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import authorize, authorize_only_admin
from app.services.topics import get_topics_service, TopicsService
from app.schemas.topics import TopicCreateData, TopicPatchData, TopicData, TopicChilds, TopicDataWithChilds
from app.db.database import get_db
from app.helpers.errors_helper import raise_if_http_error
from app.helpers.topics_helper import is_topic_progenitor

router = APIRouter()


@router.get("/topics", response_model=list[TopicData], tags=["topics"])
async def get_topics(topics_service: TopicsService = Depends(get_topics_service)):
    topics = await topics_service.get_topics()

    raise_if_http_error(topics)
    return topics


@router.get("/topics/{id}", response_model=TopicDataWithChilds, tags=["topics"])
async def get_topic(id: int, topics_service: TopicsService = Depends(get_topics_service)):
    topic = await topics_service.get_topic(id)

    raise_if_http_error(topic)
    return topic


@router.post("/topics", response_model=TopicData, tags=["topics"], description="Only for admin")
async def create_topic(topic_dto: TopicCreateData, auth=Depends(authorize_only_admin),
                       topics_service: TopicsService = Depends(get_topics_service)):
    topic = await topics_service.create_topic(topic_dto)

    raise_if_http_error(topic)
    return topic


@router.patch("/topics/{id}", response_model=TopicDataWithChilds, tags=["topics"], description="Only for admin")
async def change_topic_data(id: int, topic_dto: TopicPatchData, auth=Depends(authorize_only_admin),
                            topics_service: TopicsService = Depends(get_topics_service)):
    topic = await topics_service.change_topic_data(id, topic_dto)

    raise_if_http_error(topic)
    return topic


@router.delete("/topics/{id}", tags=["topics"], description="Only for admin")
async def delete_topic(id: int, auth=Depends(authorize_only_admin),
                       topics_service: TopicsService = Depends(get_topics_service)):
    service_response = await topics_service.delete_topic(id)

    raise_if_http_error(service_response)
    return status.HTTP_200_OK


@router.get("/topics/{id}/childs", response_model=TopicChilds, tags=["topics"])
async def get_topic_childs(id: int, topics_service: TopicsService = Depends(get_topics_service)):
    childs = await topics_service.get_topic_childs(id)

    raise_if_http_error(childs)
    return childs


@router.post("/topics/{id}/childs", response_model=TopicDataWithChilds, tags=["topics"], description="Only for admin")
async def add_childs_to_topic(id: int, childs: list[int], auth=Depends(authorize_only_admin),
                              topics_service: TopicsService = Depends(get_topics_service)):
    topic = await topics_service.add_childs_to_topic(id, childs)

    raise_if_http_error(topic)
    return topic


@router.delete("/topics/{id}/childs", response_model=TopicDataWithChilds, tags=["topics"], description="Only for admin")
async def delete_topic_childs(id: int, childs: list[int], auth=Depends(authorize_only_admin),
                              topics_service: TopicsService = Depends(get_topics_service)):
    topic = await topics_service.delete_topic_childs(id, childs)

    raise_if_http_error(topic)
    return topic
