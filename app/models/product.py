from sqlalchemy import Column, Integer, String, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR

from app.database import Base, FatherBase


class Product(FatherBase):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)

    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    category_id = Column(Integer, ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    tags = Column(ARRAY(String), server_default='{}')

    price = Column(Numeric(10, 2), nullable=False, server_default='0.00', comment="价格")
    stock = Column(Integer, nullable=False, server_default='0', comment="库存量")
    attrs = Column(JSONB, server_default='{}', comment="其他属性")

    search_vector = Column(TSVECTOR)

Index('ix_products_search_vector', Product.search_vector, postgresql_using='gin')