from flask.views import MethodView
from flask import jsonify, request, make_response
from flasgger import swag_from
# from src.models.UserRoleModel import User, Role, UserRole
from werkzeug.security import check_password_hash
from src.models.BankingModel import User, Role, UserRole
from src.config.settings import db
from src.services.AuthService import Authentication
from flask_login import login_user


class LoginView(MethodView):

    @swag_from({
    'tags': ['Authentication'],  # You can adjust the tag name
    'summary': 'User login',
    'description': 'Login endpoint that authenticates a user and returns a JWT token.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Email and password for login',
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'user@example.com'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'password123'
                    }
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful, JWT token returned',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Login successful!'
                    },
                    'token': {
                        'type': 'string',
                        'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid email or password',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid email or password!'
                    }
                }
            }
        }
    }
})
    def post(self):
        if 'email' in request.json and 'password' in request.json:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            # Find the user by email
            user = User.query.filter_by(email=email).first()
            print(user)

            if user is None or not check_password_hash(user.password_hash, password):
                return jsonify({"error": "Invalid email or password!"}), 400
            
            # Generate JWT token for the user

            if user:
                login_user(user)
                response_user = login_user(user)
                role_slugs = (
                    db.session.query(Role.slug, User.email)
                    .join(UserRole, User.id == UserRole.user_id)
                    .join(Role, UserRole.role_id == Role.id)
                    .filter(User.email == email)
                    .all()
                )
                slug = ", ".join(row.slug for row in role_slugs)
                # db.session.close_all
                token = Authentication.create_jwt_token(user.id, slug)
                
                    # Create a response
            response = make_response(jsonify({
                "message": "Login successful!",
                "token" : token,
                "response_user" : response_user
            }), 200)

            # response.set_cookie('jwt_token', token, httponly=True, secure=True)

            return response

        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']

            # Find the user by email
            user = User.query.filter_by(email=email).first()

            if user is None or not check_password_hash(user.password_hash, password):
                return jsonify({"error": "Invalid email or password!"}), 400
            
            # Generate JWT token for the user

            if user:
                role_slugs = (
                    db.session.query(Role.slug, User.email)
                    .join(UserRole, User.id == UserRole.user_id)
                    .join(Role, UserRole.role_id == Role.id)
                    .filter(User.email == email)
                    .all()
                )
                slug = ", ".join(row.slug for row in role_slugs)
                # db.session.close_all
                # token = Authentication.create_jwt_token(user.id, user.role)
                token = Authentication.create_jwt_token(user.id, slug)
                
                    # Create a response
            response = make_response(jsonify({
                "message": "Login successful!"
            }), 200)

            # response.set_cookie('jwt_token', token, httponly=True, secure=True)

            return response

        return jsonify({"error": "Invalid input!"}), 400