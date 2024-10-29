import os
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import jsonify, request
from src.models.UserRoleModel import User, Role, UserRole
from src.config.settings import db

class Authentication:
    @staticmethod
    def create_jwt_token(user_id,role_slug):
        JWT_SECRET = os.getenv('JWT_SECRET')
        payload = {
            'user_id': user_id,
            'user_role': role_slug,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)  # Token expires in 1 hour
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        # print(f"Generated Token: {token}")  # Debugging
        return token
    
    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            JWT_SECRET = os.getenv('JWT_SECRET')
            token = None
            # Check if token is passed in the Authorization header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                # print(f"Authorization header: {auth_header}")  # Debugging

                # Ensure the header starts with 'Bearer' and has two parts
                parts = auth_header.split(" ")
                if len(parts) == 2 and parts[0] == 'Bearer':
                    token = parts[1]
                else:
                    return jsonify({"error": "Invalid Authorization header format"}), 403

            if not token:
                return jsonify({"error": "Token is missing!"}), 403

            try:
                # Decode the token to get the user ID
                data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                # print(f"Decoded token data: {data}")  # Debugging the decoded token

                current_user = db.session.get(User, data['user_id'])
                if not current_user:
                    raise ValueError("User not found")
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired!"}), 403
            except jwt.InvalidTokenError as e:
                print(f"Token error: {str(e)}")  # Print the specific error message
                return jsonify({"error": "Invalid token!"}), 403

            return f(current_user, *args, **kwargs)

        return decorated

    @staticmethod
    def auth_role(required_role):    
        def decorator(f):
            @wraps(f)
            def decorated(current_user, *args, **kwargs):
                # Query to check if the current user has the required role
                user_roles = (
                    db.session.query(Role.slug, User.id)
                    .join(UserRole, User.id == UserRole.user_id)
                    .join(Role, UserRole.role_id == Role.id)
                    .filter(User.id == current_user.id)
                    .all()
                )

                role_slugs = ", ".join(role.slug for role in user_roles)

                # Check if the required role is in the user's roles
                if required_role not in role_slugs:
                    return jsonify({"error": "Unauthorized access, role mismatch!"}), 403
                db.session.close_all
                
                return f(current_user, *args, **kwargs)
            return decorated
        return decorator
       