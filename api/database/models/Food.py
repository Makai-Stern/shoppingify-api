import uuid

from database import Base
from database.relationships import CategoryFood
from decouple import config
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

DOMAIN = config("DOMAIN")


class Food(Base):

    __tablename__ = "foods"

    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        UniqueConstraint("user_id", "name"),
    )

    id = Column(
        "id", Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    image = Column(String)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # Relationships
    user_id = Column(Text, ForeignKey("users.id"))
    user = relationship("User", back_populates="foods")

    carts = relationship("CartFood", back_populates="foods")

    # User owns and maintains their own Categories
    categories = relationship(
        "Category",
        secondary=CategoryFood,
        back_populates="foods",
    )

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            image=f"{DOMAIN}{self.image}" if self.image else None,
            name=self.name,
            description=self.description,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            # if self.updated_at
            # else None
            ,
            categories=[
                jsonable_encoder(category)["name"] for category in self.categories
            ],
        )

    class Config:
        orm_mode = True
