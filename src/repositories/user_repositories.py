from fastapi_sqlalchemy import db
from ..models.all_models import User

def get_user_by_id(user_id: int):
    with db():  # db() provides the session automatically
        return db.session.query(User).filter(User.id == user_id).first()