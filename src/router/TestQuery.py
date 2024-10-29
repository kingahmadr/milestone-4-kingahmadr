from flask.views import MethodView
from flask import jsonify, request
from flasgger import swag_from
from sqlalchemy.orm import aliased
from src.models.UserRoleModel import User, Role, UserRole
from src.config.settings import db
from src.services.AuthService import Authentication

from werkzeug.security import check_password_hash

class TestQueryView(MethodView):
    def get(self):
        db.create_all
        # Aliasing the Role table to avoid conflicts
        results = (
            db.session.query(Role.slug, User.email)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .filter(User.email == 'mamad1@email.com')
            .all()
        )


        # Collecting the slugs into a list
        # role_slugs = [row.slug for row in results]
        role_slugs = ", ".join(row.slug for row in results)
        print(f'{role_slugs}')
        
        user = User.query.filter_by(email="mamad1@email.com").first()  # Get the user object
        if user:
            has_role = user.has_role('admin')  # Pass the 'admin' role to check
            print(f'has_role: {has_role}')
        else:
            print("User not found")

        db.session.close()  # Closing the session

        return jsonify({
            "role_slugs": role_slugs
        })
