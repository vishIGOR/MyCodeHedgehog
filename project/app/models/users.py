from app.db.database import Base
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    password = Column(String(), nullable=False)
    role_id = Column(Integer(), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    role = relationship("Role")

    __mapper_args__ = {"eager_defaults": True}
