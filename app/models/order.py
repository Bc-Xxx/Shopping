from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, CheckConstraint
from app.database import FatherBase


# 订单核心：订单主表 + 明细表 + 状态 CHECK + 价格快照

class Order(FatherBase):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, comment="订单总金额")
    status = Column(String(20), nullable=False, server_default='pending', comment="订单状态")

    __table_args__ = (
        CheckConstraint("status IN ('pending','paid','shipped','delivered','cancelled')",
                        name='ck_order_status'),
    )


class OrderItem(FatherBase):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, comment="购买的数量")
    unit_price = Column(Numeric(10, 2), nullable=False, comment="下单时的价格")  # ← 价格快照
