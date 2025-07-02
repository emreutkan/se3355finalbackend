from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID
from .user import User

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    
    user_id = Column(GUID(), ForeignKey('users.id'), primary_key=True)
    movie_id = Column(GUID(), ForeignKey('movies.id'), primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='watchlist')
    movie = relationship('Movie', back_populates='watchlist')
    
    def to_dict(self):
        from .movie import Movie
        return {
            'user_id': str(self.user_id),
            'movie_id': str(self.movie_id),
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'movie': self.movie.to_dict(include_actors=False) if self.movie else None
        } 