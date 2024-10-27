from fastapi import FastAPI
from .controllers import user_controllers

app = FastAPI()

# Include all routers
app.include_router(user_controllers.router)