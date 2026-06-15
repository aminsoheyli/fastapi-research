from argon2 import PasswordHasher
from sqlalchemy import Column, String, Boolean, func, Integer, DateTime
from sqlalchemy.orm import relationship

from core.database import Base

ph = PasswordHasher(
    memory_cost=65536,
    time_cost=3,
    parallelism=4,
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), nullable=False, unique=True)
    password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    tasks = relationship("TaskModel", back_populates="user")

    def hash_password(self, plain_password: str) -> str:
        """Hashes the given password using bcrypt."""
        return ph.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """Verifies the given password against the stored hash."""
        return ph.verify(hash=self.password, password=plain_password)

    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)
