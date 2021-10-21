import os
import shutil
import uuid
from typing import Optional

from database.connect import get_db
from database.models import Category, Food, User
from database.relationships import CartFood
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.middlewares import JWTBearer

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
        foods = (
            db.query(Food)
            .filter(Food.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        foods = db.query(Food).filter(Food.user_id == current_user.id).all()
    data = []
    for food in foods:
        data.append(food.to_dict())
    return data


@router.get("/{id}")
async def get_one(
    id: str, db: Session = Depends(get_db), current_user: User = Depends(JWTBearer())
):
    food = None

    try:
        uuid.UUID(str(id))
        id_is_uuid = True
    except ValueError:
        id_is_uuid = False

    if id_is_uuid:
        food = (
            db.query(Food)
            .filter(Food.id == id, Food.user_id == current_user.id)
            .first()
        )
    else:
        food = (
            db.query(Food)
            .filter(Food.name == id, Food.user_id == current_user.id)
            .first()
        )

    if food:
        return food.to_dict()

    return JSONResponse(
        content={"error": "Food does not exist."},
        status_code=400,
    )


@router.post("/")
async def create(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    categories: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    # Check if Food exists
    food_exists = (
        db.query(Food)
        .filter(Food.name == name, Food.user_id == current_user.id)
        .first()
    )

    if not food_exists:
        food = Food(name=name, user=current_user)
        if image:
            if image.filename:
                ext = os.path.splitext(image.filename)[1]
                while True:
                    # this is the closest thing to a do-while loop, in python
                    filename = uuid.uuid4().hex + ext
                    file_location = f"static/{filename}"
                    if not os.path.exists(file_location):
                        break
                # Save Image file
                with open(file_location, "wb+") as file_object:
                    shutil.copyfileobj(image.file, file_object)
                # Add Image Path to Model
                food.image = file_location
        if description:
            food.description = description
        if categories:
            categories_list = categories.split(",")
            for name in categories_list:
                category = (
                    db.query(Category)
                    .filter(Category.name == name, Category.user_id == current_user.id)
                    .first()
                )
                if category is None:
                    category = Category(name=name, user=current_user)
                # Append Category
                food.categories.append(category)

        db.add(food)
        db.commit()
        db.refresh(food)
        return food.to_dict()

    return JSONResponse(
        content={"error": f"Food '{name}', already exists."},
        status_code=400,
    )


@router.put("/{id}")
async def update(
    id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    categories: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):

    food = db.query(Food).filter(Food.id == id, Food.user_id == current_user.id).first()

    errors = {}

    if food:
        db_food_data = food.to_dict()

        if name:
            food_exists = (
                db.query(Food)
                .filter(Food.name == id, Food.user_id == current_user.id)
                .first()
            )
            if food_exists:
                errors["name"] = f"Name {name}, already exist"
                # This will be the only error
                return JSONResponse(
                    content={"error": errors},
                    status_code=400,
                )
            else:
                food.name = name
        if description:
            food.description = description
        if categories:
            categories_list = categories.split(",")
            new_categories = []
            for name in categories_list:
                category = (
                    db.query(Category)
                    .filter(Category.name == name, Category.user_id == current_user.id)
                    .first()
                )
                if category is None:
                    category = Category(name=name, user=current_user)
                # Append Category
                # food.categories.append(category)
                new_categories.append(category)
            food.categories = new_categories
        if image:
            if image.filename:
                ext = os.path.splitext(image.filename)[1]
                while True:
                    # this is the closest thing to a do-while loop, in python
                    filename = uuid.uuid4().hex + ext
                    file_location = f"static/{filename}"
                    if not os.path.exists(file_location):
                        break
                # Save Image file
                with open(file_location, "wb+") as file_object:
                    shutil.copyfileobj(image.file, file_object)

                # Get old image path
                old_image = food.image

                # Add Image Path to Model
                food.image = file_location

                # Delete old image
                try:
                    if os.path.exists(old_image):
                        os.remove(old_image)
                except OSError as e:
                    ...

        if (
            food.name != db_food_data["name"]
            or food.categories != db_food_data["categories"]
            or food.description != db_food_data["description"]
            or food.image != db_food_data["image"]
        ):
            db.commit()
            db.refresh(food)

        return food.to_dict()

    # if errors:
    #     return {"error": errors}

    return JSONResponse(
        content={"error": f"Food does not exist."},
        status_code=400,
    )


@router.delete("/{id}")
async def delete(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    db_food = (
        db.query(Food).filter(Food.id == id, Food.user_id == current_user.id).first()
    )

    if db_food:
        # Remove Food From Association Table
        db.query(CartFood).filter(CartFood.food_id == id).delete()

        db.query(Food).filter(Food.id == id, Food.user_id == current_user.id).delete()

        # Get old image path
        old_image = db_food.image

        # Delete old image
        try:
            if os.path.exists(old_image):
                os.remove(old_image)
        except OSError as e:
            ...

        db.commit()

        # Return Food Object for reference
        return db_food

    return JSONResponse(
        content={"error": "Food does not exist."},
        status_code=400,
    )
