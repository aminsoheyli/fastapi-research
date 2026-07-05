from sqlalchemy import Column, Integer, VARCHAR, Boolean

from .database import Base


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, not_null=True)
    title = Column(VARCHAR(255), nullable=False)
    body = Column(VARCHAR(255), nullable=False)
    published = Column(Boolean, nullable=False, server_default='true')
