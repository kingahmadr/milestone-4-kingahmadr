from flask import jsonify
from src.models.BankingModel import Account, Transaction
from src.config.settings import db
class Transaction_service:

    def get_all_transactions_current_user(account_id, account_type, account_number):
        transactions = Transaction.query.filter_by(from_account_id=account_id).all()
        print(f"Transactions: {transactions}")

        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                "id": transaction.id,
                "from_account_id": transaction.from_account_id,
                "to_account_id": transaction.to_account_id,
                "amount": transaction.amount,
                "created_at": transaction.created_at
            })

        return jsonify({
                "message": "All transactions",
                "account": {
                    "account_type": account_type,
                    "account_number": account_number
                },
                "transactions": transaction_list  # List of transactions
            }), 200
    
    def get_transactions_by_id(transaction_id, from_account_id):

        transaction = Transaction.query.filter_by(id=transaction_id).first()

        print(f"Transaction: {transaction}, from_account_id: {transaction.from_account_id}")

        if transaction.from_account_id != from_account_id:
            return jsonify({"message": "Transaction Not Found"}), 404
        else:
            return jsonify({
                "id": transaction.id,
                "from_account_id": transaction.from_account_id,
                "to_account_id": transaction.to_account_id,
                "amount": transaction.amount,
                "created_at": transaction.created_at
            }), 200

    def transfer_to_account(from_account_id, to_account_id, amount):
        checking_from_account_type = Account.query.filter_by(
            id=from_account_id, account_type='checking',
            is_deleted=False
            ).first()
        
        if not checking_from_account_type:
            return jsonify({"message": "Your account not allowed to transfer"}), 403
        
        if checking_from_account_type.balance < amount:
            return jsonify({"message": "Insufficient funds"}), 400

        elif checking_from_account_type.balance >= amount:
            checking_to_account_type = Account.query.filter_by(
                id=to_account_id, account_type='checking',
                is_deleted=False
                ).first()
            
            if checking_to_account_type:
                checking_from_account_type.balance -= amount

                checking_to_account_type.balance += amount
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
            else:
                return jsonify({
                    "message": "To account not found"
                }), 404

    def withdraw_from_account(from_account_id,to_account_id, amount):
        
        if from_account_id == to_account_id:
            query_account_id = Account.query.filter_by(
                id=from_account_id, is_deleted=False
                ).first()
        
            print(f"Account found: ID={query_account_id.id}, Type={query_account_id.account_type}, Is Deleted={query_account_id.is_deleted}")
               
            if query_account_id.balance < amount:
                return jsonify({"message": "Insufficient funds"}), 400

            elif query_account_id.balance >= amount:
                query_account_id.balance -= amount
                db.session.commit()

                new_transaction = Transaction(
                    from_account_id=from_account_id,
                    to_account_id=from_account_id,
                    amount=amount,
                )

                db.session.add(new_transaction)
                db.session.commit()

                return jsonify({
                    "message": "Withdraw transaction created successfully",
                    "new transaction": {
                        "id": new_transaction.id,
                        "from_account_id": new_transaction.from_account_id,
                        "to_account_id": new_transaction.to_account_id,
                        "amount": new_transaction.amount
                    }
                }), 200

        else:
            return jsonify({
                "message": "You must withdraw with the same account ID"
            }), 403

    def deposit_from_account(from_account_id, to_account_id, amount):
        if from_account_id == to_account_id:
            query_account_id = Account.query.filter_by(
                id=from_account_id, is_deleted=False
                ).first()
            print(f"Account found: ID={query_account_id.id}, Type={query_account_id.account_type}, Is Deleted={query_account_id.is_deleted}")

            query_account_id.balance += amount
            db.session.commit()

            new_transaction = Transaction(
                from_account_id=from_account_id,
                to_account_id=from_account_id,
                amount=amount,
            )

            db.session.add(new_transaction)
            db.session.commit()

            return jsonify({
                "message": "Deposit transaction created successfully",
                "new transaction": {
                    "id": new_transaction.id,
                    "from_account_id": new_transaction.from_account_id,
                    "to_account_id": new_transaction.to_account_id,
                    "amount": new_transaction.amount
                }
            }), 200
        else:
            return jsonify({
                "message": "You must Deposit with the same account ID"
            }), 403




        