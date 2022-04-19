from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    parent_id = Column(Integer(), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    parent = relationship("Topic")

    __mapper_args__ = {"eager_defaults": True}
