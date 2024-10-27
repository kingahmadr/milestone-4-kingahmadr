from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from .config import dev, prod
from .routes import app as api_app

def create_app():
    config = prod.ProdConfig()  
    app = FastAPI(title=config.APP_NAME)

    # Add DBSessionMiddleware for managing database sessions
    app.add_middleware(DBSessionMiddleware, db_url=config.DATABASE_URL)

    # Include your routers
    app.include_router(api_app.router)

    return app

app = create_app()