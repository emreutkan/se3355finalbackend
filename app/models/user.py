import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
from .guid import GUID

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for Google accounts
    full_name = Column(String(120), nullable=False)
    country = Column(String(2), nullable=True)  # ISO-3166-1 alpha-2
    city = Column(String(80), nullable=True)
    photo_url = Column(Text, nullable=True)
    auth_provider = Column(Enum('local', 'google', name='auth_provider_enum'), nullable=False, default='local')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = relationship('Rating', back_populates='user', cascade='all, delete-orphan')
    watchlist = relationship('Watchlist', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'country': self.country,
            'city': self.city,
            'photo_url': self.photo_url,
            'auth_provider': self.auth_provider,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 