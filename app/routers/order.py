from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.models import User, Product, Cart, Order, OrderItem
from app.schemas.order import OrderOut, OrderDetail, OrderItemOut
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/orders", response_model=OrderDetail)
async def create_order(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """从购物车创建订单（事务 + 行级锁）"""
    # 1. 查出购物车所有商品
    result = await db.execute(
        select(Cart, Product.name, Product.price, Product.stock)
        .join(Product, Cart.product_id == Product.id)
        .where(Cart.user_id == current_user.id)
    )
    cart_items = result.all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车是空的")

    # 2. 🔒 FOR UPDATE 锁库存（按 product_id 排序避免死锁
    product_ids = sorted([row.Cart.product_id for row in cart_items])
    result = await db.execute(
        select(Product).where(Product.id.in_(product_ids))
        .with_for_update()  # 行级锁
    )
    products = {p.id: p for p in result.scalars().all()}

    # 3. 验证库存 + 扣库存
    order_items_data = []
    total_amount = 0.0

    for row in cart_items:
        cart_item = row.Cart
        product = products[cart_item.product_id]

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"商品「{product.name}」库存不足（剩余 {product.stock}）"
            )

        product.stock -= cart_item.quantity
        unit_price = float(product.price)
        subtotal = unit_price * cart_item.quantity
        total_amount += subtotal

        order_items_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    # 4. 创建 Order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
    )
    db.add(order)
    await db.flush()  # 获取 order.id，但不提交

    # 5. 创建 OrderItem
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )
        db.add(order_item)

    # 6. 清空购物车
    await db.execute(
        delete(Cart).where(Cart.user_id == current_user.id)
    )

    # 7. 提交事务
    await db.commit()
    await db.refresh(order)

    # 8. 拼响应
    items = [
        OrderItemOut(**item) for item in order_items_data
    ]
    return OrderDetail(
        id=order.id,
        total_amount=total_amount,
        status=order.status,
        created_at=order.created_at,
        items=items,
    )


@router.get("/orders", response_model=list[OrderOut])
async def list_orders(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """查看我的订单列表"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


@router.get("/orders/{order_id}", response_model=OrderDetail)
async def get_order(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """查看订单详情"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    result = await db.execute(
        select(OrderItem, Product.name)
        .join(Product, OrderItem.product_id == Product.id)
        .where(OrderItem.order_id == order.id)
    )
    rows = result.all()
    items = []
    for row in rows:
        oi = row.OrderItem
        items.append(OrderItemOut(
            product_id=oi.product_id,
            product_name=row.name,
            quantity=oi.quantity,
            unit_price=float(oi.unit_price),
            subtotal=float(oi.unit_price) * oi.quantity,
        ))

    return OrderDetail(
        id=order.id,
        total_amount=float(order.total_amount),
        status=order.status,
        created_at=order.created_at,
        items=items,
    )
