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
    def get(self, current_user, transaction_id=None):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            account = Account.query.filter_by(user_id=active_user, is_deleted=False).first()
            print(f"Active User: {active_user}, Account: {account.id}, user_id: {account.user_id}")
            if not account:
                return jsonify({"error": "Account not found"}), 404

            if transaction_id is None:
                get_transactions, status_code = Transaction_service.get_all_transactions_current_user(account.id, account.account_type, account.account_number)
                return (get_transactions), status_code
            else:
               get_transactions_by_id, status_code = Transaction_service.get_transactions_by_id(transaction_id, account.id)
               return (get_transactions_by_id), status_code
            

        
    @login_required
    @Authentication.token_required
    def post(self, current_user):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        active_user = Authentication.get_id_from_token(token)
        if active_user:
            account = Account.query.filter_by(user_id=active_user, is_deleted=False).first()
            print(f"Active User: {active_user}, Account: {account}")
            if not account:
                return jsonify({"error": "Account not found"}), 404

            data = request.get_json()
            
            transaction_type = data.get('transaction_type')
            amount = data.get('amount')

            match transaction_type:
                case 'transfer':
                    to_account_id = data.get('to_account_id')

                    transfer_to, status_code = Transaction_service.transfer_to_account(account.id, to_account_id, amount)
            
                    return (transfer_to), status_code

                case 'withdraw':
                    From_account_id = data.get('from_account_id')
                    To_account_id = data.get('to_account_id')

                    withdraw_from, status_code = Transaction_service.withdraw_from_account(From_account_id, To_account_id, amount)

                    return (withdraw_from), status_code
                
                case 'deposit':
                    From_account_id = data.get('from_account_id')
                    To_account_id = data.get('to_account_id')

                    deposit_from, status_code = Transaction_service.deposit_from_account(From_account_id, To_account_id, amount)

                    return (deposit_from), status_code
            

