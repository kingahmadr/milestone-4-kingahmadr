from fastapi import APIRouter
from ..services.user_services import fetch_user

router = APIRouter()

@router.get("/users/{user_id}")
def read_user(user_id: int):
    user = fetch_user(user_id)
    if not user:
        return {"error": "User not found"}
    return user