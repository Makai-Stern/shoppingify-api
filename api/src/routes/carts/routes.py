import uuid

from database.connect import get_db
from database.models import Cart, Food, User
from database.relationships import CartFood
from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.middlewares import JWTBearer

from .schemas import CartSchema

router = APIRouter()


@router.get("/")
async def get_all(
    db: Session = Depends(get_db),
    page: int = None,
    limit: int = 10,
    current_user: User = Depends(JWTBearer()),
):
    if type(page) is int:
        # Page starts at 1
        skip = (page - 1) * limit
        carts = (
            db.query(Cart)
            .filter(Cart.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        carts = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    data = []
    for cart in carts:
        data.append(cart.to_dict())
    return data


@router.get("/{id}")
async def get_one(
    id: str, db: Session = Depends(get_db), current_user: any = Depends(JWTBearer())
):
    cart = None

    try:
        uuid.UUID(str(id))
        id_is_uuid = True
    except ValueError:
        id_is_uuid = False

    if id_is_uuid:
        cart = (
            db.query(Cart)
            .filter(Cart.id == id, Cart.user_id == current_user.id)
            .first()
        )
    else:
        cart = (
            db.query(Cart)
            .filter(Cart.name == id, Cart.user_id == current_user.id)
            .first()
        )

    if cart:
        return Cart.to_dict()

    return JSONResponse(
        content={"error": "Cart does not exist."},
        status_code=400,
    )


@router.put("/{id}")
async def update(
    id: str,
    cart: CartSchema = Body(...),
    db: Session = Depends(get_db),
    current_user: any = Depends(JWTBearer()),
):
    db_cart = (
        db.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
    )

    # cart_data = db_cart.to_dict()
    cart_data = (
        db.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
    )

    if db_cart:
        for var, value in vars(cart).items():
            index = 1
            if str(var) == "foods":
                new_foods = []
                for name in cart.foods:
                    food = (
                        db.query(Food)
                        .filter(Food.name == name, Food.user_id == current_user.id)
                        .first()
                    )
                    if food:

                        association = (
                            db.query(CartFood)
                            .filter(
                                CartFood.cart_id == db_cart.id,
                                CartFood.food_id == food.id,
                            )
                            .first()
                        )

                        if not association:
                            # Create association
                            association = CartFood(
                                food_qty=1,
                                cart_id=db_cart.id,
                                user_id=current_user.id,
                                food_id=food.id,
                            )
                            db.add(association)

                        if association not in new_foods:
                            new_foods.append(association)
                        elif association in new_foods:
                            index += 1
                            association_index = new_foods.index(association)
                            association_obj = new_foods[association_index]
                            # association_obj.food_qty += 1
                            association_obj.food_qty = index

                db_cart.foods = new_foods
            else:
                setattr(db_cart, var, value) if value or str(value) == "False" else None
        if (
            db_cart.name != cart_data.name
            or db_cart.status != cart_data.status
            or db_cart.foods != cart_data.foods
        ):
            db.commit()
            db.refresh(db_cart)
        return db_cart.to_dict()

    return JSONResponse(
        content={"error": "Cart does not exist."},
        status_code=400,
    )


@router.post("/")
async def create(
    cart: CartSchema = Body(...),
    db: Session = Depends(get_db),
    current_user: any = Depends(JWTBearer()),
):
    cart_exists = (
        db.query(Cart)
        .filter(Cart.name == cart.name, Cart.user_id == current_user.id)
        .first()
    )

    if not cart_exists:
        new_cart = Cart(name=cart.name, status=cart.status, user=current_user)

        if cart.foods:
            for name in cart.foods:
                food = (
                    db.query(Food)
                    .filter(Food.name == name, Food.user_id == current_user.id)
                    .first()
                )
                if food:
                    association = CartFood(
                        food_qty=1,
                        cart_id=new_cart.id,
                        user_id=current_user.id,
                        food_id=food.id,
                    )

                    if association not in new_cart.foods:
                        db.add(association)
                        new_cart.foods.append(association)
                    elif association in new_cart.foods:
                        association_index = new_cart.foods.index(association)
                        association_obj = new_cart.foods[association_index]
                        association_obj.food_qty += 1

        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart.to_dict()

    return JSONResponse(
        content={"error": f"Cart '{cart.name}', already exists."},
        status_code=400,
    )


@router.delete("/{id}")
async def delete(
    id: str,
    db: Session = Depends(get_db),
    current_user: any = Depends(JWTBearer()),
):
    db_cart = (
        db.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
    )
    if db_cart:
        db.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).delete()
        db.commit()
        return db_cart
    return JSONResponse(
        content={"error": "Cart does not exist."},
        status_code=400,
    )
