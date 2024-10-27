from ..repositories.user_repositories import get_user_by_id

def fetch_user(user_id: int):
    return get_user_by_id(user_id)