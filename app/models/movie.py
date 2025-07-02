import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, SmallInteger, Numeric, Date, DateTime, Enum, CheckConstraint, Index, desc
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID
from .movie_actor import MovieActor
from .rating import Rating
from .watchlist import Watchlist
from .popularity_snapshot import PopularitySnapshot

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    title_tr = Column(String(255), nullable=True)
    original_title = Column(String(255), nullable=True)
    year = Column(SmallInteger, nullable=False)
    summary = Column(Text, nullable=False)
    summary_tr = Column(Text, nullable=True)
    imdb_score = Column(Numeric(3, 1), default=0.0)  # Cached average
    metascore = Column(SmallInteger, nullable=True)
    trailer_url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    runtime_min = Column(SmallInteger, nullable=True)
    release_date = Column(Date, nullable=True)
    language = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('year >= 1888', name='valid_year'),
        CheckConstraint('imdb_score >= 0 AND imdb_score <= 10', name='valid_score'),
        CheckConstraint('metascore >= 0 AND metascore <= 100', name='valid_metascore'),
        Index('idx_movies_title_search', 'title'),
        Index('idx_movies_year', 'year'),
    )
    
    # Relationships
    actors = relationship('MovieActor', back_populates='movie', cascade='all, delete-orphan')
    ratings = relationship('Rating', back_populates='movie', cascade='all, delete-orphan')
    watchlist = relationship('Watchlist', back_populates='movie', cascade='all, delete-orphan')
    popularity_snapshots = relationship('PopularitySnapshot', back_populates='movie', cascade='all, delete-orphan')
    categories = relationship('MovieCategory', back_populates='movie', cascade='all, delete-orphan')
    
    def to_dict(self, include_actors=True, include_popularity=True):
        from .actor import Actor
        from .popularity_snapshot import PopularitySnapshot

        result = {
            'id': str(self.id),
            'title': self.title,
            'title_tr': self.title_tr,
            'original_title': self.original_title,
            'year': self.year,
            'summary': self.summary,
            'summary_tr': self.summary_tr,
            'imdb_score': float(self.imdb_score) if self.imdb_score else 0.0,
            'metascore': self.metascore,
            'trailer_url': self.trailer_url,
            'image_url': self.image_url,
            'runtime_min': self.runtime_min,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'categories': [mc.category.name for mc in self.categories]
        }
        
        if include_actors:
            result['actors'] = [ma.actor.to_dict() for ma in self.actors]

        if include_popularity:
            latest_snapshot = db.session.query(PopularitySnapshot).filter_by(
                movie_id=self.id
            ).order_by(desc(PopularitySnapshot.snapshot_date)).first()
            
            if latest_snapshot:
                result['popularity'] = latest_snapshot.to_dict()
            else:
                result['popularity'] = None
        
        return result