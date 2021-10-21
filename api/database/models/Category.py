import uuid

from database import Base
from database.relationships import CategoryFood
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Category(Base):

    __tablename__ = "categories"

    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        UniqueConstraint("user_id", "name"),
    )

    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # Relationships
    user_id = Column(Text, ForeignKey("users.id"))
    user = relationship("User", back_populates="categories")
    foods = relationship("Food", secondary=CategoryFood, back_populates="categories")

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            description=self.description,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            # if self.updated_at
            # else None
            ,
            foods=[jsonable_encoder(food)["name"] for food in self.foods],
        )

    class Config:
        orm_mode = True
