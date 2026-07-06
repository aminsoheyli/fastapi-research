from sqlalchemy import Column, Integer, VARCHAR, Boolean, TIMESTAMP, text

from .database import Base


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(255), nullable=False)
    content = Column(VARCHAR(255), nullable=False)
    published = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
