from flask.views import MethodView
from flask import jsonify, request, render_template, redirect, url_for
from src.models.BankingModel import User, Role, Account
from src.config.settings import db
from flasgger import swag_from
from werkzeug.security import generate_password_hash
from src.services.Validator import Validator
from src.services.AuthService import Authentication


class AccountView(MethodView):
    
    @Authentication.token_required
    def post(self, current_user):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            data = request.get_json()
            accountType = data.get('account_type')
            accountNumber = data.get('account_number')
            balance = data.get('balance')

            existing_account_type = db.session.query(Account).filter_by(account_type=accountType).first()
            if existing_account_type:
                return jsonify({"error": "Account type already exists"}), 400

            new_account = Account(
                user_id=active_user,
                account_type=accountType,
                account_number=accountNumber,
                balance=balance
            )

            db.session.add(new_account)
            db.session.commit()


            return jsonify({
                "message": "Account created successfully",
                "new account": new_account
            }), 201

