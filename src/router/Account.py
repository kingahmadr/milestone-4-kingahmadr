from flask.views import MethodView
from flask import jsonify, request
from flask_login import login_required
from src.models.BankingModel import User, Account
from src.config.settings import db
# from flasgger import swag_from
from src.services.AuthService import Authentication


class AccountView(MethodView):

    @login_required
    @Authentication.token_required
    def get(self, current_user, account_id=None):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
            
        if account_id is None:
            active_user = Authentication.get_id_from_token(token)
            if active_user:
                result = db.session.query(
                    User.id,
                    User.username,
                    User.email,
                    Account.id,
                    Account.account_number,
                    Account.account_type,
                    Account.balance
                ).join(Account, User.id == Account.user_id).filter(User.id == active_user, Account.is_deleted == False).all()

                user_data_account = []
                for row in result:
                    user_data_account.append({
                        'user_id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'account_id': row[3],
                        'account_number': row[4],
                        'account_type': row[5],
                        'balance': row[6]
                    })

                return jsonify(user_data_account), 200
        else:
            active_user = Authentication.get_id_from_token(token)
            if active_user:
                result = db.session.query(
                    User.id,
                    User.username,
                    User.email,
                    Account.id,
                    Account.account_number,
                    Account.account_type,
                    Account.balance
                ).join(Account, User.id == Account.user_id).filter(User.id == active_user, Account.id == account_id, Account.is_deleted == False).all()

                user_data_account = []
                for row in result:
                    user_data_account.append({
                        'user_id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'account_id': row[3],
                        'account_number': row[4],
                        'account_type': row[5],
                        'balance': row[6]
                    })
                if user_data_account == []:
                    return jsonify({"message": "Account ID Not Found"}), 404
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
    
    @login_required
    @Authentication.token_required
    def put(self, current_user, account_id):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            data = request.get_json()
            Account_Number = data.get('account_number')

            # account = Account.query.get(account_id).filter(user_id=active_user).first()
            account = Account.query.filter_by(id=account_id, user_id=active_user).first()
            if not account:
                return jsonify({"error": "Account not found"}), 404

            account.account_number = Account_Number
            db.session.commit()

            return jsonify({
                "message": "Account updated successfully",
                "updated account": {
                    "id": account.id,
                    "user_id": account.user_id,
                    "account_number": account.account_number
               
                }
            }), 200
    
    @login_required
    @Authentication.token_required
    def delete(self, current_user,account_id):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            account = Account.query.filter_by(id=account_id, user_id=active_user, is_deleted=False).first()
            if not account:
                return jsonify({"error": "Account not found"}), 404

            # db.session.delete(account)
            account.is_deleted = True
            db.session.commit()

            return jsonify({"message": "Account deleted successfully"}), 200
