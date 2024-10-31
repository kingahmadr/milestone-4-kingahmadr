# config/settings.py

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder
import os
from dotenv import load_dotenv
from flasgger import Swagger

# Load environment variables
load_dotenv()

# Initialize the database and migration objects (but don't attach them to the app yet)
db = SQLAlchemy()
migrate = Migrate()
seeder = FlaskSeeder()

def create_app(settings_conf=None):
    """Application factory to create a Flask app instance."""
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    print("Template folder:", template_dir)
    print("Static folder:", static_dir)

    # Swagger configuration for securityDefinitions
    swagger_config = {
        "swagger": "2.0",
        "title": "Mad API Flask Bank Api Milestone 4",
        "description": "API documentation with JWT authentication",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        # Include the 'specs' key to resolve KeyError
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",  # URL for accessing the Swagger UI
        # Add a headers key to prevent TypeError
        "headers": []
    }
   
    # Load configuration
    swagger = Swagger(app, config=swagger_config)

    os.environ.setdefault("FLASK_SETTINGS_MODULE", "src.config.prod")
    conf = settings_conf or os.getenv("FLASK_SETTINGS_MODULE")
    app.config.from_object(conf)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = "ThisIsASecretKey"


    # Initialize the app with extensions
    db.init_app(app)
    migrate.init_app(app, db)
    seeder.init_app(app, db)

    from src.router.Login import LoginView
    from src.router.Logout import LogoutView
    # from src.router.UserFetch import UserFetchView
    from src.router.User import UserView
    from src.router.Account import AccountView
    from src.router.Transaction import TransactionView
    # from src.router.Review import ReviewView
    # from src.router.TestQuery import TestQueryView
    from src.models.BankingModel import User
    from flask_login import LoginManager

    login_manager = LoginManager(app)
    # login_manager.login_view = "/"  # Set the login view endpoint name

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    login_view = LoginView.as_view('login_view')
    app.add_url_rule('/auth/v1/login', view_func=login_view, methods=['GET','POST'])
    app.add_url_rule('/auth/v1/login/<int:user_id>', view_func=login_view, methods=['GET'])

    logout_view = LogoutView.as_view('logout_view')
    app.add_url_rule('/auth/v1/logout', view_func=logout_view, methods=['GET','POST'])
    

    user_view = UserView.as_view('user_view')
    app.add_url_rule('/v1/user', view_func=user_view, methods=['POST'])
    app.add_url_rule('/v1/user/me', view_func=user_view, methods=['GET','PUT'])

    account_view = AccountView.as_view('account_view')
    app.add_url_rule('/v1/accounts', view_func=account_view, methods=['POST','GET'])
    app.add_url_rule('/v1/accounts/<int:account_id>', view_func=account_view, methods=['GET','PUT','DELETE'])
    # app.add_url_rule('/v1/account/me', view_func=account_view, methods=['GET'])

    transaction_view = TransactionView.as_view('transaction_view')
    app.add_url_rule('/v1/transactions', view_func=transaction_view, methods=['POST','GET'])
    app.add_url_rule('/v1/transactions/<int:transaction_id>', view_func=transaction_view, methods=['GET'])


    

    # test_query_view = TestQueryView.as_view('test_query_view')
    # app.add_url_rule('/v2/getquery', view_func=test_query_view, methods=['GET'])
    
    @app.route('/')
    def hello_from_api():
        return 'Mad API v2'
    
    @app.route('/create-all-db')
    def create_all_db():
        db.create_all()
        return jsonify({'message': 'Database created successfully'})
    
    @app.route('/test-template')
    def test_template():
        print("Template folder: ", app.template_folder)
        return render_template('login.html')

    return app