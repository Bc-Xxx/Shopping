from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Text, CheckConstraint
from sqlalchemy.orm import relationship

from app.database import Base, FatherBase


class User(FatherBase):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('buyer', 'seller', 'admin')", name='ck_user_role'),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hash_password = Column(String(100), nullable=False)
    avatar = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, server_default='true')
    role = Column(String(20), nullable=False, default='buyer', server_default='buyer')

    products = relationship('Product', backref='seller')
