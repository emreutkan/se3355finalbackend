import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .. import db
from .guid import GUID

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True, index=True)
    
    movies = relationship('MovieCategory', back_populates='category', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name
        } 