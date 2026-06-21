from pydantic import BaseModel
from datetime import datetime


class OrderItemOut(BaseModel):
    """订单明细响应"""
    product_id: int
    product_name: str
    quantity: int
    unit_price: float  # 下单时的价格
    subtotal: float  # 总价格

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    """订单列表响应"""
    id: int
    total_amount: float  # 订单总金额
    status: str  # 订单状态
    created_at: datetime

    class Config:
        from_attributes = True


class OrderDetail(OrderOut):
    """订单详情响应（订单信息 + 明细列表）"""
    items: list[OrderItemOut]
