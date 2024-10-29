from flask.views import MethodView
from flask import jsonify, request, render_template, make_response
from flasgger import swag_from
from src.models.UserRoleModel import User, Role, UserRole
from src.config.settings import db
from src.services.AuthService import Authentication
from flask_login import login_user, login_required

from werkzeug.security import check_password_hash

class LoginView(MethodView):

    # def get(self):
    #     msg=''
    #     return render_template('login.html', msg = msg)
    @swag_from({
            'tags':['Authentication'],
            'summary':'Get User Data',
            'parameters':[
                {
                    'name': 'user_id',
                    'in': 'path',
                    'type': 'integer',
                    'required': False,
                    'description': 'ID of the users to retrieve'
                }
            ],
            'responses': {
                200:{
                    'description':'user(s) retrived successfully',
                    'schema':{
                        'type':'object',
                        'properties':{
                            'Users': {
                                'type':'array',
                                'items':{
                                    'type':'object',
                                    'properties':{
                                        'id': {
                                            'type': 'integer',
                                            'example': 1
                                        },
                                        'username': {
                                            'type':'string',
                                            'example': 'mamad'
                                        },
                                        'email': {
                                            'type': 'email',
                                            'example': 'mamad@email.com'
                                        },
                                        'password_hash':{
                                            'type':'string',
                                            'example':'<Encrypted Password with Hash algorithm>'
                                        }
                                    }
                                    
                                }
                            }
                        }
                    }
                },
                404:{
                    'description': 'User not found',
                    'schema':{
                        'type':'object',
                        'properties':{
                            'error':{
                                'type': 'string',
                                'example': 'User not found'
                            }
                        }
                    }
                }
            }

        })
    @login_required
    def get(self, user_id=None):
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
                db.session.close_all
                # token = Authentication.create_jwt_token(user.id, user.role)
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
                db.session.close_all
                # token = Authentication.create_jwt_token(user.id, user.role)
                token = Authentication.create_jwt_token(user.id, slug)
                
                    # Create a response
            response = make_response(jsonify({
                "message": "Login successful!"
            }), 200)

            response.set_cookie('jwt_token', token, httponly=True, secure=True)

            return response

        return jsonify({"error": "Invalid input!"}), 400