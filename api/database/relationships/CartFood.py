from database import Base, SessionLocal
from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, Text
from sqlalchemy.orm import relationship


class CartFood(Base):
    __tablename__ = "carts_foods"

    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        PrimaryKeyConstraint("cart_id", "food_id"),
    )

    cart_id = Column(Text, ForeignKey("carts.id"))
    user_id = Column(Text, ForeignKey("users.id"))
    food_id = Column(Text, ForeignKey("foods.id"))

    food_qty = Column(Integer)
    foods = relationship("Food", back_populates="carts")
    carts = relationship("Cart", back_populates="foods")

    def get_food_name(self):
        # This import causes issues on the top-level, but it is not a circular dependency.
        from database.models import Food

        db = SessionLocal()
        food = db.query(Food).filter(Food.id == self.food_id).first()
        if food:
            return food.name
        return None

    def to_dict(self):
        return dict(
            food_id=self.food_id,
            food_name=self.get_food_name(),
            food_qty=self.food_qty,
        )

    def __eq__(self, association):
        return (
            self.cart_id == association.cart_id and self.food_id == association.food_id
        )
