from flasgger import swag_from
from flask.views import MethodView
from flask import jsonify, request, redirect, url_for
from flask_login import login_required
from src.models.BankingModel import User, Role, UserRole
from src.config.settings import db
from werkzeug.security import generate_password_hash
from src.services.Validator import Validator
from src.services.AuthService import Authentication


class UserView(MethodView):

    @swag_from({
        'tags': ['User'],  # Group under Authentication tag
        'summary': 'Get current user',
        'description': 'Endpoint to get the current user with an username, email, role.',
        'security': [{'Bearer': []}],  # Include Bearer token authentication
        'responses': {
            '200': {
                'description': 'User found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'example': 1
                        },
                        'username': {
                            'type': 'string',
                            'example': 'username1'
                        },
                        'email': {
                            'type': 'string',
                            'example': 'user@example.com'
                        },
                        'role': {
                            'type': 'string',
                            'example': 'admin'
                        }
                    }
                }
            },
            '401': {
                'description': 'Unauthorized access',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Unauthorized'
                        }
                    }
                }
            }
        }
    })
    @login_required
    @Authentication.token_required
    def get(self, current_user):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            user_data = db.session.query(
                User.id,
                User.username,
                User.email,
                Role.slug
            ).join(
                UserRole, User.id == UserRole.user_id
            ).join(
                Role, UserRole.role_id == Role.id
            ).filter(
                User.id == active_user
            ).first()
            print(f"{user_data}")
            if user_data:
                return jsonify({
                    'id': user_data.id,
                    'username': user_data.username,
                    'email': user_data.email,
                    'role': user_data.slug
                }), 200
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'message': 'Unauthorized'}), 401

    @swag_from({
    'tags': ['User'],  # Group under Authentication tag
    'summary': 'User registration',
    'description': 'Endpoint to register a new user with an username, email, password and role.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Email, Username, password for user registration',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'username21'
                    },
                    'email': {
                        'type': 'string',
                        'example': 'newuser@example.com'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'password123'
                    },
                    'role': {
                        'type': 'string',
                        'example': 'user'
                    }
                },
                'required': ['username','email', 'password','role']
            }
        }
    ],
    # 'security': [{'Bearer': []}],  # Include Bearer token authentication
    'responses': {
        201: {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'User registered successfully!'
                    }
                }
            }
        },
        400: {
            'description': 'User already exists or invalid input',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'User already exists!'
                    }
                }
            }
        }
    }
})

    # def post(self):
    #     data = request.json if request.is_json else request.form
        
    #     # Check for required fields
    #     if all(field in data for field in ['username', 'email', 'password']):
    #         username = data.get('username')
    #         email = data.get('email')
    #         password = data.get('password')
    #         role_name = data.get('role')

    #         # Check if user already exists
    #         if User.query.filter_by(email=email).first():
    #             return jsonify({"error": "User with this email already exists!"}), 400
            
    #         if User.query.filter_by(username=username).first():
    #             return jsonify({"error": "User with this username already exists!"}), 400

    #         # Validate email
    #         email_input, status_code = Validator.email_validation(email_request=email)
    #         if status_code != 200:
    #             return jsonify(email_input), status_code

    #         # Hash the password and create the user
    #         hashed_password = generate_password_hash(password)
    #         new_user = User(username=username, email=email, password_hash=hashed_password)

    #         # Assign role if it exists
    #         if role_name:
    #             role = Role.query.filter_by(slug=role_name).first()
    #             if role:
    #                 new_user.roles.append(role)
    #             else:
    #                 return jsonify({"error": f"Role '{role_name}' not found!"}), 400

    #         # Save new user to the database
    #         db.session.add(new_user)
    #         db.session.commit()

    #         if request.is_json:
    #             return jsonify({"message": "User registered successfully!"}), 201
    #         else:
    #             return redirect(url_for('login_view'))
    #     else:
    #         return jsonify({"error": "Missing required fields: username, email, or password."}), 400

    def post(self):
        # data = request.json  
        # return jsonify({"message": "User registered successfully!"}), 201

        if 'username' in request.json and 'email' in request.json and 'password' in request.json and 'role' in request.json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role_name = data.get('role')

            if User.query.filter_by(email=email).first():
                # return jsonify({"error": "User already exists!"}), 400
                return jsonify({"error": "User with this email already exists!"}), 400

            email_input, status_code = Validator.email_validation(email)

            if status_code == 200:
                # Hash the user's password and create a new user
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, email=email, password_hash=hashed_password)
                
                # Find the role and add to the user
                role = Role.query.filter_by(slug=role_name).first()  # Query role by slug
                if role:
                    new_user.roles.append(role)  # Append the actual Role object
                else:
                    return jsonify({"error": f"Role '{role_name}' not found!"}), 400

                db.session.add(new_user)
                db.session.commit()
                
                return jsonify({"message": "User registered successfully!"}), 201
                # return (email_input), status_code
            else:
                return (email_input), status_code
                
        if 'username' in request.form and 'email' in request.form and 'password' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role_name = request.form['role']
        
            # User checking in database
            if User.query.filter_by(email=email).first():
                return jsonify({"error": "User already exists!"}), 400

            email_input, status_code = Validator.email_validation(email_request=email)

            if status_code == 200:
                # Hash the user's password and create a new user
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, email=email, password_hash=hashed_password)
                
                # Find the role and add to the user
                role = Role.query.filter_by(slug=role_name).first()  # Query role by slug
                if role:
                    new_user.roles.append(role)  # Append the actual Role object
                else:
                    return jsonify({"error": f"Role '{role_name}' not found!"}), 400

                db.session.add(new_user)
                db.session.commit()
                
                return redirect(url_for('login_view'))
            else:
                return jsonify(email_input), status_code
            
    @swag_from({
        'tags': ['User'],
        'summary': 'Update current user',
        'description': 'Update current user',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'description': 'username, email, password for user update',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                            'example': 'username1'
                        },
                        'email': {
                            'type': 'string',
                            'example': 'newuser@example.com'
                        },
                        'password': {
                            'type': 'string',
                            'example': 'password123'
                        }
                    },
                }
            }
        ],
        'security': [{'Bearer': []}],  # Include Bearer token authentication
        'responses': {
            200: {
                'description': 'User updated successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'User updated successfully!'
                        }
                    }
                }
            },
            400: {
                'description': 'Username or email already exists',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Username already exists!'
                        }
                    }
                }
            },
            404: {
                'description': 'User not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'User not found!'
                        }
                    }
                }
            }
        }
    })
    @login_required
    @Authentication.token_required
    def put(self, current_user):
    # def put(self):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password_user= data.get('password')

            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != active_user:
                return jsonify({"error": "Username already exists"}), 400

            # Check if email already exists
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != active_user:
                return jsonify({"error": "Email already exists"}), 400
            
            user = User.query.get(active_user)
            # user = User.query.filter_by(email='mamad4@email.com').first()
            # print(user)
            # return jsonify({"error": "User not found"}), 404
            if user:
                if password_user:
                    user.username = username
                    user.email = email
                    user.password_hash = generate_password_hash(password_user)
                    db.session.commit()
                    return jsonify({"message": "User updated successfully"}), 200
                else:
                    user.username = username
                    user.email = email
                    db.session.commit()
                    return jsonify({"message": "User updated successfully"}), 200
            
            else:
                return jsonify({"error": "User not found"}), 404

        



