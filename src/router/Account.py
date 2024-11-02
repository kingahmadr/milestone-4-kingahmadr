from flask.views import MethodView
from flask import jsonify, request
from flask_login import login_required
from src.models.BankingModel import User, Account
from src.config.settings import db
from flasgger import swag_from
# from flasgger import swag_from
from src.services.AuthService import Authentication


class AccountView(MethodView):

    @swag_from({
        'tags': ['Account'],
        'summary': 'Get user accounts',
        'description': 'Retrieve accounts for the current user.',
        'parameters': [
            {
                'name': 'account_id',
                'in': 'path',
                'required': False,
                'description': 'ID of the account to retrieve details for',
                'schema': {
                    'type': 'integer',
                    'example': 1
                }
            }
        ],
        'security': [{'Bearer': []}],
        'responses': {
            '200': {
                'description': 'List of user accounts',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'user_id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'email': {'type': 'string'},
                            'account_id': {'type': 'integer'},
                            'account_number': {'type': 'string'},
                            'account_type': {'type': 'string'},
                            'balance': {'type': 'number'}
                        }
                    }
                }
            },
            '401': {
                'description': 'Unauthorized access',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
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
            
    
    @swag_from({
        'tags': ['Account'],
        'summary': 'Create a new account',
        'description': 'Create a new account for the current user.',
        'consumes': [
            'application/json'
        ],
        'parameters': [
            {
                'name': 'account_type',
                'in': 'body',
                'description': 'Type of account',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'account_type': {
                            'type': 'string',
                            'example': 'checking'
                        },
                        'account_number': {
                            'type': 'string',
                            'example': '1234567890'
                        },
                        'balance': {
                            'type': 'number',
                            'example': 1000.00
                        }
                    }
                }
            },
            # {
            #     'name': 'account_number',
            #     'in': 'body',
            #     'description': 'Unique account number',
            #     'required': True,
            #     'schema': {
            #         'type': 'string',
            #         'example': '1234567890'
            #     }
            # },
            # {
            #     'name': 'balance',
            #     'in': 'body',
            #     'description': 'Balance of the account',
            #     'required': True,
            #     'schema': {
            #         'type': 'number',
            #         'example': 1000.00
            #     }
            # }
        ],
        'security': [{'Bearer': []}],
        'responses': {
            '201': {
                'description': 'Account created successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'new account': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'user_id': {'type': 'integer'},
                                'account_type': {'type': 'string'},
                                'account_number': {'type': 'string'},
                                'balance': {'type': 'number'}
                            }
                        }
                    }
                }
            },
            '400': {
                'description': 'Bad request',
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
    
    @swag_from({
        'tags': ['Account'],
        'summary': 'Update existing account',
        'description': 'Update existing account',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'description': 'Account number to update',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'account_number': {
                            'type': 'string',
                            'example': '1234567890'
                        }
                    },
                    'required': ['account_number']
                }
            },
            {
                'name': 'account_id',
                'in': 'path',
                'required': True,
                'description': 'ID of the account to update',
                'schema': {
                    'type': 'integer',
                    'example': 1
                }
            }
        ],
        'security': [{'Bearer': []}],  # Include Bearer token authentication
        'responses': {
            200: {
                'description': 'Account updated successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Account updated successfully!'
                        },
                        'updated account': {
                            'type': 'object',
                            'properties': {
                                'id': {
                                    'type': 'integer',
                                    'example': 1
                                },
                                'user_id': {
                                    'type': 'integer',
                                    'example': 1
                                },
                                'account_number': {
                                    'type': 'string',
                                    'example': '1234567890'
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Account not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Account not found'
                        }
                    }
                }
            }
        }
    })
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
    
    
    @swag_from({
        'tags': ['Account'],
        'summary': 'Delete account',
        'description': 'Delete account for the current user.',
        'parameters': [
            {
                'name': 'account_id',
                'in': 'path',
                'required': True,
                'description': 'ID of the account to delete',
                'schema': {
                    'type': 'integer',
                    'example': 1
                }
            }
        ],
        'security': [{'Bearer': []}],
        'responses': {
            '200': {
                'description': 'Account deleted successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Account deleted successfully'
                        }
                    }
                }
            },
            '404': {
                'description': 'Account not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Account not found'
                        }
                    }
                }
            }
        }
    })
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
