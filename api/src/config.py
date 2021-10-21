import os

from decouple import config
from pydantic import BaseSettings

# Routes
from src.routes import auth_router, carts_router, foods_router, users_router, categories_router


def initialize_routes(app):
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(users_router, prefix="/api/users")
    app.include_router(foods_router, prefix="/api/foods")
    app.include_router(carts_router, prefix="/api/carts")
    app.include_router(categories_router, prefix="/api/categories")



class Settings(BaseSettings):
    APP_NAME: str = config("APP_NAME")
    DEBUG_MODE: bool = config("DEBUG_MODE")
    HOST: str = config("HOST")
    PORT: int = config("PORT")


settings = Settings()
