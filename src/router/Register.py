from flask.views import MethodView
from flask import jsonify, request, render_template, redirect, url_for
from src.models.UserRoleModel import User, Role
from src.config.settings import db
from flasgger import swag_from
from werkzeug.security import generate_password_hash


class RegisterView(MethodView):

    def get(self):
        msg=''
        return render_template('register.html', msg=msg)

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

                # return jsonify({"message": "User registered successfully!"}), 201
                
                return redirect(url_for('login_view'))
            # return jsonify({"message": "User registered successfully!"}), 201
            else:
                return jsonify(email_input), status_code

        



