# seed_database.py

from src.models.UserRoleModel import Role
from src.config.settings import db
from flask_seeder import Seeder

class RoleSeeder(Seeder):
    def run(self):
        # Create the roles
        roles = [
            Role(name="Administrator", slug="admin"),
            Role(name="Super Administrator", slug="super-admin")
        ]
        
        # Add roles to the session
        for role in roles:
            # Check if the role already exists to avoid duplicates
            if not Role.query.filter_by(slug=role.slug).first():
                db.session.add(role)
                print(f"Added role: {role.name}")
            else:
                print(f"Role {role.name} already exists")

        # Commit the session to save roles in the database
        db.session.commit()
