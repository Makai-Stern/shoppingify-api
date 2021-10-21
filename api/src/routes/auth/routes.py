from typing import Optional

import bcrypt
from database.connect import get_db
from database.models import User
from fastapi import APIRouter, Body, Depends, Response
from fastapi.encoders import jsonable_encoder
from fastapi.params import Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.middlewares import JWTBearer
from src.utils import signJWT

from .schemas import AuthUserSchema

router = APIRouter()


@router.post("/register")
def register(user: AuthUserSchema = Body(...), db: Session = Depends(get_db)):

    errors = {}
    # Check if user already exists
    email_exists = db.query(User).filter(User.email == user.email).first()
    username_exists = db.query(User).filter(User.username == user.username).first()

    # Error Handling
    if email_exists:
        errors["email"] = "Email is taken."

    if username_exists:
        errors["username"] = "Username is taken."

    if len(errors):
        return JSONResponse(
            content={"error": {**errors}},
            status_code=400,
        )

    # Hashed Password
    password = user.password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # entered_password = entered_password.encode("utf-8")
    # When checking the password > if bcrypt.hashpw(entered_password, hashed_password) == hashed_password:

    # Create User
    new_user = User(username=user.username, email=user.email, password=hashed_password)

    # Save User to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Omit Password
    user_data = jsonable_encoder(new_user)
    user_data.pop("password", None)
    return user_data


@router.get("/whoami")
async def whoami(
    response: Response,
    current_user: any = Depends(JWTBearer(auto_error=False)),
) -> dict:

    if current_user:
        user = current_user.to_dict()
        return user
    else:
        response.delete_cookie(key="token")
        response.status_code = 403
        return {"error": "Not Authorized."}


@router.post("/login")
async def login(
    response: Response,
    user: AuthUserSchema = Body(...),
    db: Session = Depends(get_db),
    token: Optional[str] = Cookie(None),
) -> dict:

    if token:
        response.delete_cookie(key="token")

    # Generic Response for a unsuccessful attempt / user does not exist
    not_authenticated = JSONResponse(
        content={"error": "Username or Password invalid"},
        status_code=400,
    )

    db_user = None
    # Check if user exists in database

    if user.email:
        db_user = db.query(User).filter(User.email == user.email).first()
    elif user.username:
        db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        return not_authenticated

    # Compare Passwords
    # entered_password = entered_password.encode("utf-8")
    # When checking the password > if bcrypt.hashpw(entered_password, hashed_password) == hashed_password:
    password = user.password.encode("utf-8")
    hashed_password = db_user.password

    authorized = bcrypt.hashpw(password, hashed_password) == hashed_password

    user_data = jsonable_encoder(db_user)

    # Sign User Id as a JWT Token
    if authorized:
        jwt_token = signJWT(user_data)
    else:
        return not_authenticated

    # Set the JWT token as a cookie
    response.set_cookie(key="token", value=jwt_token, httponly=True)

    # Omit the password from the response
    user_data.pop("password", None)

    # Return the user's data
    return user_data


@router.get("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(key="token")
    return {"Success"}


# This is made for the front end:
@router.post("/password")
async def update_password(
    user: AuthUserSchema = Body(...),
    current_user: any = Depends(JWTBearer()), 
    db: Session = Depends(get_db)
) -> dict:
    if user.newPassword:
        current_password = user.password.encode("utf-8")
        hashed_password = current_user.password
        authorized = bcrypt.hashpw(current_password, hashed_password) == hashed_password

        if authorized:
            new_password = user.newPassword.encode("utf-8")
            hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
            current_user.password = hashed_password
            db.commit()
            return "Success, password updated."
        else:
            return JSONResponse(
                content={"error": {"currentPassword": "Password is incorrect."}},
                status_code=400,
            )

    return JSONResponse(
        content={"error": "Changes could not be processed."},
        status_code=400,
    )
