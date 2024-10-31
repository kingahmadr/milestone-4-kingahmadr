from flask.views import MethodView
from flask import jsonify, request
from flask_login import login_required
from flasgger import swag_from
from src.models.BankingModel import Account
# from src.config.settings import db
# from flasgger import swag_from
from src.services.AuthService import Authentication
from src.services.TransactionService import Transaction_service


class TransactionView(MethodView):

    @swag_from({
        'tags': ['Transaction'],
        'summary': 'Get all transaction for the current user',
        'description': 'Retrieve all transactions for the current user.',
        'parameters': [
            {
                'name': 'transaction_id',
                'in': 'path',
                'required': False,
                'description': 'ID of the transaction to retrieve details for',
                'schema': {
                    'type': 'integer',
                    'example': 1
                }
            }
        ],
        'security': [{'Bearer': []}],
        'responses': {
            '200': {
                'description': 'List of transactions',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'from_account_id': {'type': 'integer'},
                            'to_account_id': {'type': 'integer'},
                            'amount': {'type': 'number'},
                            'created_at': {'type': 'string'}
                        }
                    }
                }
            },
            '401': {
                'description': 'Unauthorized access',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            '404': {
                'description': 'Account not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
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
            
    @swag_from({
    'tags': ['Transaction'],
    'summary': 'Create a new transaction',
    'description': 'Create a new transaction for the current user (transfer, withdraw, or deposit).',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'description': 'Transaction details',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'transaction_type': {
                        'type': 'string',
                        'enum': ['transfer', 'withdraw', 'deposit'],
                        'description': 'Type of transaction',
                        'example': 'transfer'
                    },
                    'amount': {
                        'type': 'number',
                        'description': 'Amount for the transaction',
                        'example': 1000.00
                    },
                    'to_account_id': {
                        'type': 'integer',
                        'description': 'ID of the account to transfer to (only for transfer)',
                        'example': 2
                    },
                    'from_account_id': {
                        'type': 'integer',
                        'description': 'ID of the account to withdraw from or deposit to',
                        'example': 1
                    }
                },
                'required': ['transaction_type', 'amount']
            }
        }
    ],
    'security': [{'Bearer': []}],
    'responses': {
        '200': {
            'description': 'Transaction processed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'transaction': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'from_account_id': {'type': 'integer'},
                            'to_account_id': {'type': 'integer'},
                            'amount': {'type': 'number'},
                            'created_at': {'type': 'string'}
                        }
                    }
                }
            }
        },
        '400': {
            'description': 'Invalid input data',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        },
        '404': {
            'description': 'Account not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        '401': {
            'description': 'Unauthorized access',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
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

            # Ensure we correctly parse the JSON request data
            try:
                data = request.get_json()
                if not isinstance(data, dict):
                    return jsonify({"error": "Invalid input format, expected a JSON object"}), 400
            except Exception as e:
                return jsonify({"error": "Unable to parse JSON", "details": str(e)}), 400
                
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
            

