from flask.views import MethodView
from flask import jsonify
# from flasgger import swag_from
from src.models.UserRoleModel import User, Role, UserRole
from src.config.settings import db

class UserFetchView(MethodView):
    def get(self, user_id=None):
        db.create_all()

        print(f'{db}')
        user_fields = ['id', 'username','email', 'password_hash']

        if user_id is None:
            # users = User.query.all()
            user_details = (
                    db.session.query(User.id, User.username, User.email, User.password_hash, Role.slug)
                    .join(UserRole, User.id == UserRole.user_id)
                    .join(Role, UserRole.role_id == Role.id)    
                    .all()
                )
            # results = [{field: getattr(user, field) for field in fields} for user in users]
            results = [
                {**{field: row[i] for i, field in enumerate(user_fields)}, 'role': row[4]}
                for row in user_details
            ]

            return jsonify({"Users":results})
        else:
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            # user_data = {field: getattr(user, field) for field in fields}
            user_detail = (
                db.session.query(User.id, User.username, User.email, User.password_hash, Role.slug)
                .join(UserRole, User.id == UserRole.user_id)
                .join(Role, UserRole.role_id == Role.id)
                .filter(User.id == user_id)
                .all()
            )
            results = [
                {**{field: row[i] for i, field in enumerate(user_fields)}, 'role': row[4]}
                for row in user_detail
            ]
            

            return jsonify(results)
