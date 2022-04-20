from typing import Optional
from pydantic import BaseModel, constr


class TopicCreateData(BaseModel):
    name: constr(min_length=1, max_length=50)
    description: constr(min_length=1, max_length=500)
    parent_id: Optional[int] = None


class TopicData(BaseModel):
    id: int
    name: str
    description: str
    parent_id: Optional[int] = None


class TopicChilds(BaseModel):
    childs: list[TopicData]


class TopicDataWithChilds(TopicChilds, TopicData):
    pass


class TopicPatchData(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    description: Optional[constr(min_length=1, max_length=500)] = None
    parent_id: Optional[int] = None
