from sqlalchemy import Column, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID

class MovieActor(db.Model):
    __tablename__ = 'movie_actors'
    
    movie_id = Column(GUID(), ForeignKey('movies.id'), primary_key=True)
    actor_id = Column(GUID(), ForeignKey('actors.id'), primary_key=True)
    order_index = Column(SmallInteger, nullable=False, default=0)  # Billing order
    
    # Relationships
    movie = relationship('Movie', back_populates='actors')
    actor = relationship('Actor', back_populates='movies')
    
    def to_dict(self):
        return {
            'movie_id': str(self.movie_id),
            'actor_id': str(self.actor_id),
            'order_index': self.order_index,
            'actor': self.actor.to_dict() if self.actor else None
        } 