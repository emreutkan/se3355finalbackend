from datetime import datetime
from sqlalchemy import Column, Date, Numeric, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID

class PopularitySnapshot(db.Model):
    __tablename__ = 'popularity_snapshots'
    
    movie_id = Column(GUID(), ForeignKey('movies.id'), primary_key=True)
    snapshot_date = Column(Date, primary_key=True, default=datetime.utcnow().date)
    score = Column(Numeric(8, 2), nullable=False, default=0.0)
    rank = Column(SmallInteger, nullable=True)  # Materialized ranking
    
    # Relationships
    movie = relationship('Movie', back_populates='popularity_snapshots')
    
    def to_dict(self):
        return {
            'movie_id': str(self.movie_id),
            'snapshot_date': self.snapshot_date.isoformat() if self.snapshot_date else None,
            'score': float(self.score),
            'rank': self.rank
        } 