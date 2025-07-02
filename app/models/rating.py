import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, SmallInteger, DateTime, CheckConstraint, Index, ForeignKey
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    movie_id = Column(GUID(), ForeignKey('movies.id'), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    voter_country = Column(String(2), nullable=False)  # From user profile
    helpful_yes_count = Column(SmallInteger, nullable=False, default=0)
    helpful_no_count = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 10', name='valid_rating'),
        Index('idx_rating_movie_user', 'movie_id', 'user_id'),
        Index('idx_rating_country', 'voter_country'),
    )
    
    # Relationships
    movie = relationship('Movie', back_populates='ratings')
    user = relationship('User', back_populates='ratings')
    
    def to_dict(self, include_user=True):
        result = {
            'id': str(self.id),
            'movie_id': str(self.movie_id),
            'user_id': str(self.user_id),
            'rating': self.rating,
            'comment': self.comment,
            'voter_country': self.voter_country,
            'helpful_yes_count': self.helpful_yes_count,
            'helpful_no_count': self.helpful_no_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_user and self.user:
            result['user'] = {
                'full_name': self.user.full_name,
                'country': self.user.country
            }
        
        return result 