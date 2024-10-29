from datetime import datetime, timezone
from flask_login import UserMixin
from src.config.settings import db
from email_validator import validate_email, EmailNotValidError
from flask import jsonify


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone=timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone=timezone.utc))

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f'<User {self.username}>'

    accounts = db.relationship('Account', back_populates='user')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone=timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone=timezone.utc))

    def __init__(self, name,slug):
        self.name = name
        self.slug = slug
    def __repr__(self):
        return f'<Role {self.slug}>'

    users = db.relationship("User", secondary="user_roles", back_populates="roles")

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone=timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone=timezone.utc))

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self): 
        return f'<UserRole {self.user_id} {self.role_id}>'

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
    




class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone=timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone=timezone.utc))

    def __init__(self, user_id, balance):
        self.user_id = user_id
        self.balance = balance

    def __repr__(self):
        return f'<Account {self.user_id}>'
    
     # One account can have many transactions
    transactions_from = db.relationship('Transaction', foreign_keys='Transaction.from_account_id', back_populates='from_account')
    transactions_to = db.relationship('Transaction', foreign_keys='Transaction.to_account_id', back_populates='to_account')
    

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone=timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone=timezone.utc))

    def __init__(self, account_id, amount):
        self.account_id = account_id
        self.amount = amount

    def __repr__(self):
        return f'<Transaction {self.account_id}>'

    