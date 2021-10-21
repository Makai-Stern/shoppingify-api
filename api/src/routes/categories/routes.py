import uuid

from database.connect import get_db
from database.models import Category, User
from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.middlewares import JWTBearer

from .schemas import CategorySchema

router = APIRouter()


@router.post("/")
async def create(
    category: CategorySchema = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    category_exists = (
        db.query(Category)
        .filter(Category.name == category.name, Category.user_id == current_user.id)
        .first()
    )

    if not category_exists:
        new_category = Category(name=category.name, user=current_user)

        if category.description:
            new_category.description = category.description

        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category.to_dict()

    return JSONResponse(
        content={"error": f"Category '{category.name}', already exists."},
        status_code=400,
    )


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
        categories = (
            db.query(Category)
            .filter(Category.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        categories = (
            db.query(Category).filter(Category.user_id == current_user.id).all()
        )
    data = []
    for category in categories:
        data.append(category.to_dict())
    return data


@router.get("/{id}")
async def get_one(
    id: str, db: Session = Depends(get_db), current_user: User = Depends(JWTBearer())
):
    categories = None

    try:
        uuid.UUID(str(id))
        id_is_uuid = True
    except ValueError:
        id_is_uuid = False

    if id_is_uuid:
        category = (
            db.query(Category)
            .filter(Category.id == id, Category.user_id == current_user.id)
            .first()
        )
    else:
        category = (
            db.query(Category)
            .filter(Category.name == id, Category.user_id == current_user.id)
            .first()
        )

    if category:
        return category.to_dict()

    return JSONResponse(
        content={"error": "Category does not exist."},
        status_code=400,
    )


@router.put("/{id}")
async def update(
    id: str,
    category: CategorySchema = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    db_category = (
        db.query(Category)
        .filter(Category.id == id, Category.user_id == current_user.id)
        .first()
    )
    db_category_data = jsonable_encoder(db_category)

    if db_category:
        for var, value in vars(category).items():
            setattr(db_category, var, value) if value or str(value) == "False" else None

        if (
            db_category.name != db_category_data["name"]
            or db_category.description != db_category_data["description"]
        ):
            db.commit()
            db.refresh(db_category)
        return db_category.to_dict()

    return JSONResponse(
        content={"error": "Category does not exist."},
        status_code=400,
    )


@router.delete("/{id}")
async def delete(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    db_category = (
        db.query(Category)
        .filter(Category.id == id, Category.user_id == current_user.id)
        .first()
    )
    if db_category:
        db.query(Category).filter(
            Category.id == id, Category.user_id == current_user.id
        ).delete()
        db.commit()
        return db_category
    return JSONResponse(
        content={"error": "Category does not exist."},
        status_code=400,
    )
