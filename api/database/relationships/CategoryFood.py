from database import Base
from sqlalchemy import Column, ForeignKey, Integer, Table, Text

CategoryFood = Table(
    "category_foods",
    Base.metadata,
    Column("category_id", Text, ForeignKey("categories.id")),
    Column("food_id", Text, ForeignKey("foods.id")),
)
