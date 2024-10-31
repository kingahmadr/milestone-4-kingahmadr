from flask import jsonify
from sqlalchemy import or_
from src.models.BankingModel import Account, Transaction
from src.config.settings import db
class Transaction_service:

    # def __init__(self, amount):
    #     self.amount = amount

    def checking_account_type(user_id):
        checking_account_type = Account.query.filter_by(
            user_id=user_id, account_type='checking',
            is_deleted=False
            ).first()

        return checking_account_type.account_type

    def saving_account_type(user_id):
        saving_account_type = Account.query.filter_by(
            user_id=user_id, account_type='saving',
            is_deleted=False
            ).first()

        return saving_account_type.account_type
    
    def transfer_to_account(from_account_id, to_account_id, amount):
        checking_account_type = Account.query.filter_by(
            id=from_account_id, account_type='checking',
            is_deleted=False
            ).first()
        
        if not checking_account_type:
            return jsonify({"message": "Your account not allowed to transfer"}), 403
        
        if checking_account_type.balance < amount:
            return jsonify({"message": "Insufficient funds"}), 400

        elif checking_account_type.balance >= amount:
            checking_account_type.balance -= amount
            checkint_to_account_type = Account.query.filter_by(
                id=to_account_id, account_type='checking',
                is_deleted=False
                ).first()
            
            checkint_to_account_type.balance += amount
            db.session.commit()

            new_transaction = Transaction(
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
            )

            db.session.add(new_transaction)
            db.session.commit()

            return jsonify({
                "message": "Transfer transaction created successfully",
                "new transaction": {
                    "id": new_transaction.id,
                    "from_account_id": new_transaction.from_account_id,
                    "to_account_id": new_transaction.to_account_id,
                    "amount": new_transaction.amount
                }
            }), 200

    def withdraw_from_account(from_account_id, amount):
        # checking_account_type = Account.query.filter_by(
        #     id=from_account_id, account_type='checking',
        #     is_deleted=False
        #     ).first()
        checking_account_type = Account.query.filter(
                Account.id == from_account_id,
                or_(Account.account_type == 'checking', Account.account_type == 'saving'),
                Account.is_deleted == False
            ).first()
        
        print(f"Account found: ID={checking_account_type.id}, Type={checking_account_type.account_type}, Is Deleted={checking_account_type.is_deleted}")
        return jsonify({
            "message": checking_account_type.account_type,
            "amount" : amount
            }), 200
        
        # if not checking_account_type:
        #     return jsonify({"message": "Your account not allowed to withdraw"}), 403
        
        # if checking_account_type.balance < amount:
        #     return jsonify({"message": "Insufficient funds"}), 400

        # elif checking_account_type.balance >= amount:
        #     checking_account_type.balance -= amount
        #     db.session.commit()

        #     new_transaction = Transaction(
        #         from_account_id=from_account_id,
        #         to_account_id=from_account_id,
        #         amount=amount,
        #     )

        #     db.session.add(new_transaction)
        #     db.session.commit()

        #     return jsonify({
        #         "message": "Witdraw transaction created successfully",
        #         "new transaction": {
        #             "id": new_transaction.id,
        #             "from_account_id": new_transaction.from_account_id,
        #             "to_account_id": new_transaction.to_account_id,
        #             "amount": new_transaction.amount
        #         }
        #     })



        