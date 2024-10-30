from flask.views import MethodView
from flask import jsonify, request, redirect, url_for
from flask_login import login_required
from src.models.BankingModel import User, Role, UserRole
from src.config.settings import db
from flasgger import swag_from
from werkzeug.security import generate_password_hash
from src.services.Validator import Validator
from src.services.AuthService import Authentication


class UserView(MethodView):

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
    'tags': ['Authentication'],  # Group under Authentication tag
    'summary': 'User registration',
    'description': 'Endpoint to register a new user with an username, email, password and role.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Email and password for user registration',
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
                    },
                    'role': {
                        'type': 'string',
                        'example': 'admin'
                    }
                },
                'required': ['username','email', 'password','role']
            }
        }
    ],
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

    def post(self):
        # data = request.json        

        if 'username' in request.json and 'email' in request.json and 'password' in request.json:       
            data = request.json
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role_name = data.get('role')

            # User checking in database
            if User.query.filter(email == email, username == username).first():
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

                return jsonify({"message": "User registered successfully!"}), 201
            else:
                return(email_input), status_code
                
        if 'username' in request.form and 'email' in request.form and 'password' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role_name = request.form['role']
        
            # User checking in database
            if User.query.filter_by(email=email).first():
                return jsonify({"error": "User already exists!"}), 400

            email_input, status_code = User.email_validation(email_request=email)

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

    @Authentication.token_required
    def put(self, current_user):
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
            if user:
                user.username = username
                user.email = email
                user.password_hash = generate_password_hash(password_user)
                db.session.commit()
                return jsonify({"message": "User updated successfully"}), 200
            else:
                return jsonify({"error": "User not found"}), 404

        



