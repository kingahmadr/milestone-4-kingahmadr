from datetime import datetime, timezone
from src.config.settings import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False ,nullable=False)
    description = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f'<Review {self.id, self.product, self.rating, self.description}>'
    
    
