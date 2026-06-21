from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.models import User, Product, Cart
from app.schemas.cart import CartAdd, CartUpdate, CartOut, CartList
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/cart", response_model=CartOut)
async def add_to_cart(
        cart_data: CartAdd,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. 验证商品存在
    result = await db.execute(select(Product).where(Product.id == cart_data.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 2. 查购物车有没有同款
    result = await db.execute(
        select(Cart).where(
            Cart.user_id == current_user.id,
            Cart.product_id == cart_data.product_id,
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item:
        cart_item.quantity += cart_data.quantity
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=cart_data.product_id,
            quantity=cart_data.quantity,
        )
        db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)

    # 拼 CartOut 响应（需要商品名和单价)
    cart_item.product_name = product.name
    cart_item.price = float(product.price)
    cart_item.subtotal = float(product.price) * cart_item.quantity
    return cart_item


@router.get("/cart", response_model=CartList)
async def list_cart(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """查看购物车列表"""
    result = await db.execute(
        select(Cart, Product.name, Product.price)
        .join(Product, Cart.product_id == Product.id)
        .where(Cart.user_id == current_user.id)
        .order_by(Cart.created_at.desc())
    )
    rows = result.all()

    items = []
    total = 0.0
    for row in rows:
        price = float(row.price)
        qty = row.Cart.quantity
        subtotal = price * qty
        total += subtotal
        items.append(
            CartOut(
                product_id=row.Cart.product_id,
                product_name=row.name,
                price=price,
                quantity=qty,
                subtotal=subtotal,
            )
        )
    return CartList(items=items, total=total)


@router.put("/cart/{product_id}", response_model=CartOut)
async def update_cart_quantity(
        product_id: int,
        cart_data: CartUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """修改购物车中某商品的数量"""
    result = await db.execute(
        select(Cart).where(
            Cart.product_id == product_id,
            Cart.user_id == current_user.id,
        )
    )
    cart_item = result.scalar_one_or_none()
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车中没有该商品")

    cart_item.quantity = cart_data.quantity
    await db.commit()
    await db.refresh(cart_item)

    # 拼响应
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one()
    cart_item.product_name = product.name
    cart_item.price = float(product.price)
    cart_item.subtotal = float(product.price) * cart_item.quantity
    return cart_item


@router.delete("/cart/{product_id}")
async def remove_from_cart(
        product_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """删除购物车中某商品"""
    result = await db.execute(
        select(Cart).where(
            Cart.product_id == product_id,
            Cart.user_id == current_user.id,
        )
    )
    cart_item = result.scalar_one_or_none()
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车中没有该商品")

    await db.delete(cart_item)
    await db.commit()
    return {"detail": "已删除"}


@router.delete("/cart")
async def clear_cart(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """清空购物车"""
    await db.execute(
        delete(Cart).where(Cart.user_id == current_user.id)
    )
    await db.commit()
    return {"detail": "购物车已清空"}
