from flask.views import MethodView
from flask import jsonify, request
from flask_login import login_required
from src.models.BankingModel import Account, Transaction
from src.config.settings import db
# from flasgger import swag_from
from src.services.AuthService import Authentication
from src.services.TransactionService import Transaction_service


class TransactionView(MethodView):
    @login_required
    @Authentication.token_required
    def post(self, current_user):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            account = Account.query.filter_by(user_id=active_user, is_deleted=False).first()
            if not account:
                return jsonify({"error": "Account not found"}), 404

            data = request.get_json()
            
            transaction_type = data.get('transaction_type')
            amount = data.get('amount')
            to_account_id = data.get('to_account_id')

            match transaction_type:
                case 'transfer':
                    transfer_to, status_code = Transaction_service.transfer_to_account(account.id, to_account_id, amount)
            
                    return (transfer_to), status_code

                case 'withdraw':
                    withdraw_from, status_code = Transaction_service.withdraw_from_account(account.id, amount)

                    return (withdraw_from), status_code
            

