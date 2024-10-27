from sqlalchemy import Column, Integer, String, DateTime, text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from src.models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))  # Unique constraint removed for password hash
    created_at = Column(DateTime(timezone=True), server_default=text("NOW() AT TIME ZONE 'Asia/Jakarta'"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("NOW() AT TIME ZONE 'Asia/Jakarta'"))

    accounts = relationship("Account", back_populates="user")

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Use table name as string
    account_type = Column(String(255), index=True)
    account_number = Column(String(255), unique=True, index=True)
    balance = Column(DECIMAL(10, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW() AT TIME ZONE 'Asia/Jakarta'"))
    updated_at = Column(DateTime(timezone=True), onupdate=text("NOW() AT TIME ZONE 'Asia/Jakarta'"))

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)  # Use table name as string
    to_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)  # Use table name as string
    amount = Column(DECIMAL(10, 2))
    type = Column(String(255))
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW() AT TIME ZONE 'Asia/Jakarta'"))

    account = relationship("Account", back_populates="transactions")
