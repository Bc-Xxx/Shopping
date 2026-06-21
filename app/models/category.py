from app.database import FatherBase
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship


class Category(FatherBase):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
