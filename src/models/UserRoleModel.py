from datetime import datetime, timezone
from flask_login import UserMixin
from src.config.settings import db
from email_validator import validate_email, EmailNotValidError
from flask import jsonify


class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, index=True)
    email = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    roles = db.relationship("Role", secondary="user_roles", back_populates="users")

    def __repr__(self):
        return f'<User {self.id, self.username, self.email, self.password_hash}>'
    
    def has_role(self, role):
        return bool(
            Role.query
            .join(Role.users)
            .filter(User.id == self.id)
            .filter(Role.slug == role)
            .count() == 1
        )

    
    # Flask-Login methods
    def get_id(self):
        return str(self.id)
    def email_validation(email_request):
        
        try:
            # Check that the email address is valid
            emailinfo = validate_email(email_request, check_deliverability=False)

            # Get the normalized form of the email address
            normalized_email = emailinfo.normalized

            # print(f'{normalized_email}')

            return jsonify({"email": normalized_email}), 200

        except EmailNotValidError as e:
            # Handle invalid email input with a specific error message
            # print(str(e))
            return jsonify({"error": "Invalid email", "message": str(e)}), 400

    
class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)

    # Define the relationship to users table
    users = db.relationship("User", secondary="user_roles", back_populates="roles")
    
class UserRole(db.Model):
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
    
