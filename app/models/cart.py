from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, CheckConstraint

from app.database import FatherBase


class Cart(FatherBase):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, server_default='1', comment="购物车中商品的数量")

    # 唯一复合约束 + 数量 >= 1
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_cart_user_product'),
        CheckConstraint('quantity >= 1', name='ck_cart_quantity'),
    )
