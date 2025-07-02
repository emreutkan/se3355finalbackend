from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID

class MovieCategory(db.Model):
    __tablename__ = 'movie_categories'
    
    movie_id = Column(GUID(), ForeignKey('movies.id'), primary_key=True)
    category_id = Column(GUID(), ForeignKey('categories.id'), primary_key=True)
    
    # Relationships
    movie = relationship('Movie', back_populates='categories')
    category = relationship('Category', back_populates='movies') 