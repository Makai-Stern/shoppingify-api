import uuid

from database import Base
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    email = Column(String, index=True, unique=True)
    username = Column(String, index=True, unique=True)
    password = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    foods = relationship(
        "Food",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )

    carts = relationship(
        "Cart",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )

    categories = relationship(
        "Category",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )

    def to_dict(self):
        return dict(
            id=self.id,
            username=self.username,
            email=self.email,
            password=self.password,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    class Config:
        orm_mode = True
