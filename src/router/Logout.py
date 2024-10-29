from flask.views import MethodView
from flask import jsonify, make_response
from flasgger import swag_from
from flask_login import logout_user

class LogoutView(MethodView):
    @swag_from({
        'tags': ['Authentication'],
        'summary': 'User Logount',
        'description': 'Logs out the user by clearing the JWT token cookie.',
        'responses': {
                    200: {
                        'description': 'Logout successful response',
                        'content': {
                            'application/json': {
                                'example': {
                                    'message': 'Logout successful!'
                                }
                            }
                        }
                    }
                }
    })
    def get(self):
        # Create a response object
        # Clear the JWT token cookie by setting it to an empty value
        logout_response = logout_user()

        response = make_response(jsonify({
            "message": "Logout successful!",
            "logout response": logout_response
        }), 200)

        # response.set_cookie('jwt_token', '', max_age=0, expires=0)
        # response.set_cookie('session', '', max_age=0, expires=0)
        #  # Clear any other headers or cookies related to authentication
        # response.headers['Authorization'] = ''  # Example if you use a header-based token
        logout_user()
        response.delete_cookie('session')  # Adjust for the name of your session cookie, if any

        return response
    def post(self):
        logout_response = logout_user()

        response = make_response(jsonify({
            "message": "Logout successful!",
            "logout response": logout_response
        }), 200)

        # response.set_cookie('jwt_token', '', max_age=0, expires=0)
        # response.set_cookie('session', '', max_age=0, expires=0)
        #  # Clear any other headers or cookies related to authentication
        # response.headers['Authorization'] = ''  # Example if you use a header-based token
        response.delete_cookie('session')  # Adjust for the name of your session cookie, if any
        logout_user()

        return response

