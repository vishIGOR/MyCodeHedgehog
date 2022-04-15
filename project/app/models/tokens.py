from app.db.database import Base
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    token = Column(String(), nullable=False)
    user_id = Column(Integer(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True)
    user = relationship("User")


    __mapper_args__ = {"eager_defaults": True}
