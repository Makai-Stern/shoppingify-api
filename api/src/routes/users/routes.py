import bcrypt
from database.connect import get_db
from database.models import User
from fastapi import APIRouter, Body, Depends, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.middlewares import JWTBearer

from .schemas import UserSchema

router = APIRouter()


@router.put("/{id}")
async def update(
    id: str,
    user: UserSchema = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    db_user = db.query(User).filter(User.id == id).first()
    db_user_data = jsonable_encoder(db_user)
    errors = {}

    if db_user:
        if db_user.id == current_user.id:
            for var, value in vars(user).items():
                # if
                if user.email and str(var) == "email":
                    # Check if email exists
                    email_exists = db.query(User).filter(User.email == user.email).first()
                    if email_exists:
                        errors['email'] = 'Email is taken.' if email_exists.id != current_user.id else 'You are currently using this email address.'
                    else:
                        # Set Attribute
                        setattr(db_user, var, value) if value or str(
                            value
                        ) == "False" else None 
                elif user.username and str(var) == "username":
                    # Check if username exists
                    username_exists = db.query(User).filter(User.username == user.username).first()
                    if username_exists:
                        errors['username'] = 'Username is taken.' if username_exists.id != current_user.id else 'You are currently using this username.'
                    else:
                        # Set Attribute
                        setattr(db_user, var, value) if value or str(
                            value
                        ) == "False" else None 
                elif user.password and str(var) == "password":
                    password = value.encode("utf-8")
                    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                    setattr(db_user, var, hashed_password)
                else:
                    setattr(db_user, var, value) if value or str(
                        value
                    ) == "False" else None

        if errors:
            return JSONResponse(
                content={"error": {**errors}},
                status_code=400,
            )

        commit = False
        # If changes were made:
        if (
            db_user.username != db_user_data["username"]
            or db_user.email != db_user_data["email"]
        ):
            commit = True

        if not commit and db.user_data["password"]:
            if (
                not bcrypt.hashpw(db.user_data["password"], db_user.password)
                == db_user.password
            ):
                commit = True

        if commit:
            db.commit()
            db.refresh(db_user)

        return db_user.to_dict()

    return JSONResponse(
        content={"error": "User does not exist."},
        status_code=400,
    )


@router.get("/{id}")
async def get_one(
    id: str, db: Session = Depends(get_db), current_user: User = Depends(JWTBearer())
):
    db_user = db.query(User).filter(User.id == id).first()
    if db_user:
        if db_user.id == current_user.id:
            return db_user.to_dict()

    return JSONResponse(
        content={"error": "User does not exist."},
        status_code=400,
    )


@router.delete("/{id}")
async def delete(
    id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTBearer()),
):
    db_user = db.query(User).filter(User.id == id).first()
    if db_user:
        db_user_data = db_user.to_dict()
        if db_user.id == current_user.id:
            db.query(User).filter(User.id == id).delete()
            db.commit()
            response.delete_cookie(key="token")
            return db_user_data

    return JSONResponse(
        content={"error": "User does not exist."},
        status_code=400,
    )
