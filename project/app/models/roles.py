from app.db.database import Base
from sqlalchemy import Integer, String, Column


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(30), unique=True, nullable=False)

    __mapper_args__ = {"eager_defaults": True}