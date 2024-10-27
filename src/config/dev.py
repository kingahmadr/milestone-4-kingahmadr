from .base import BaseConfig
import os

class DevConfig(BaseConfig):
    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DB_STAGING_URI")