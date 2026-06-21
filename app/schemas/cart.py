from pydantic import BaseModel


class CartAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    quantity: int


class CartOut(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int  # 数量
    subtotal: float  # 小计 = price * quantity

    class Config:
        from_attributes = True  # 允许从 ORM 对象读取


class CartList(BaseModel):
    items: list[CartOut]  # 商品列表
    total: float  # 购物车总金额
