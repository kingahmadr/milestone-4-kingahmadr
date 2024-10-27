from pydantic_settings import BaseSettings
import os

class BaseConfig(BaseSettings):
    APP_NAME: str = "FastAPI MVC App"
    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DB_PROD_URI")

    class Config:
        env_file = ".env"
        extra = 'allow'