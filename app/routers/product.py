from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func, text
from app.models.category import Category

from app.database import get_db
from app.models import Product, User
from app.schemas.product import ProductOut, ProductCreate, ProductUpdate, PaginatedProducts, SearchResult
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/products", response_model=ProductOut, description="创建新商品")
async def create_product(
        product: ProductCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != 'seller':
        raise HTTPException(status_code=403, detail="只有卖家才能创建商品")
    new_product = Product(
        name=product.name,
        description=product.description,
        seller_id=current_user.id,
        category_id=product.category_id,
        tags=product.tags,
        price=product.price,
        search_vector=func.to_tsvector('simple', product.name + ' ' + product.description),
        stock=product.stock,
        attrs=product.attrs,
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@router.get("/products", response_model=PaginatedProducts, description="按列表查看商品")
async def list_products(
        skip: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            Product,
            Category.name.label("category_name"),
            func.count().over().label("total"),
        )
        .outerjoin(Category, Product.category_id == Category.id)
        .order_by(Product.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    rows = (await db.execute(query)).all()

    if not rows:
        return PaginatedProducts(total=0, items=[])

    total = rows[0].total
    items = []
    for row in rows:
        product = row[0]
        product.category_name = row.category_name
        items.append(product)

    return PaginatedProducts(total=total, items=items)


@router.get("/products/search", response_model=SearchResult, description="按内容搜索商品")
async def search_products(
        q: str = Query(..., min_length=1, description="搜索关键词"),
        skip: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db),
):
    ts_query = func.plainto_tsquery('simple', q)
    ts_condition = Product.search_vector.op('@@')(ts_query)

    # 查总数
    count_query = select(func.count()).select_from(Product).where(ts_condition)
    total = (await db.execute(count_query)).scalar() or 0

    # 查结果 + 关联分类名 + 按相关性排序
    query = (
        select(Product, Category.name.label("category_name"),
               func.ts_rank(Product.search_vector, ts_query).label("rank"))
        .outerjoin(Category, Product.category_id == Category.id)
        .where(ts_condition)
        .order_by(text("rank DESC"))
        .offset(skip).limit(limit)
    )
    rows = (await db.execute(query)).all()

    items = []
    for row in rows:
        product = row[0]
        product.category_name = row.category_name
        items.append(product)

    return SearchResult(total=total, items=items)


@router.get("/products/{id}", description="按id搜索商品")
async def get_product(
        id: int,
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="找不到这个商品")
    return product


@router.delete("/products/{id}", description="按id删除商品")
async def delete_product(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != 'seller':
        raise HTTPException(status_code=403, detail="只有卖家才能删除商品")
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="找不到这个商品")
    await db.delete(product)
    await db.commit()
    return "删除成功"


@router.put("/products/{id}", response_model=ProductOut, description="按id修改商品")
async def update_product(
        id: int,
        product_data: ProductUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != 'seller':
        raise HTTPException(status_code=403, detail="只有卖家才能修改商品")
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="找不到这个商品")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的商品")

    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    if 'name' in update_data or 'description' in update_data:
        product.search_vector = func.to_tsvector(
            'simple', product.name + ' ' + product.description
        )

    await db.commit()
    await db.refresh(product)
    return product
