from .base import BaseConfig
import os

class ProdConfig(BaseConfig):
    DATABASE_URL: str = os.getenv("DB_PROD_URI")