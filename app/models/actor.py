import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, DateTime
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID

class Actor(db.Model):
    __tablename__ = 'actors'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(120), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    photo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    movies = relationship('MovieActor', back_populates='actor', cascade='all, delete-orphan')
    
    def to_dict(self, include_movies=False):
        from .movie import Movie
        result = {
            'id': str(self.id),
            'full_name': self.full_name,
            'bio': self.bio,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'photo_url': self.photo_url
        }
        
        if include_movies:
            result['movies'] = [ma.movie.to_dict(include_actors=False) for ma in self.movies]
        
        return result 