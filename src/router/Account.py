from flask.views import MethodView
from flask import jsonify, request
from src.models.BankingModel import User, Account
from src.config.settings import db
# from flasgger import swag_from
from src.services.AuthService import Authentication


class AccountView(MethodView):

    @Authentication.token_required
    def get(self, current_user):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            result = db.session.query(
                User.id,
                User.username,
                User.email,
                Account.account_number,
                Account.account_type,
                Account.balance
            ).join(Account, User.id == Account.user_id).filter(User.id == active_user).all()

            user_data_account = []
            for row in result:
                user_data_account.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'account_number': row[3],
                    'account_type': row[4],
                    'balance': row[5]
                })

            return jsonify(user_data_account), 200
    
    @Authentication.token_required
    def post(self, current_user):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            data = request.get_json()
            Account_Type = data.get('account_type')
            Account_Number = data.get('account_number')
            balance = data.get('balance')

            existing_account_type = Account.query.filter(Account.account_number == Account_Number).first()
            if existing_account_type:
                return jsonify({"error": "Account number already exists"}), 400

            new_account = Account(
                user_id=active_user,
                account_type=Account_Type,
                account_number=Account_Number,
                balance=balance
            )

            db.session.add(new_account)
            db.session.commit()


            return jsonify({
                "message": "Account created successfully",
                "new account": {
                    "id": new_account.id,
                    "user_id": new_account.user_id,
                    "account_type": new_account.account_type,
                    "account_number": new_account.account_number,
                    "balance": new_account.balance
                }
            }), 201

