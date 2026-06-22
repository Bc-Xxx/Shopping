from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import User
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from ..utils.security import require_roles
from app.utils.redis import get_cache, set_cache, delete_cache

router = APIRouter()


@router.post("/categories", response_model=CategoryOut)
async def create_category(
        category: CategoryCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["admin"])),
):
    # if current_user.role != 'admin':
    #     raise HTTPException(status_code=403, detail="只有管理员才能创建分类")
    result = await db.execute(select(Category).where(Category.name == category.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="分类名已存在")
    if category.parent_id is not None:
        result = await db.execute(select(Category).where(Category.id == category.parent_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="父分类不存在")

    new_category = Category(name=category.name, parent_id=category.parent_id)
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    await delete_cache("categories:list")
    return new_category


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(
        db: AsyncSession = Depends(get_db),
):
    # 1. 先查缓存
    cached = await get_cache("categories:list")
    if cached:
        return cached
    # 2. 缓存没命中 → 查 DB
    result = await db.execute(select(Category).order_by(Category.id.asc()))
    categories = result.scalars().all()
    # 3. 写回缓存（TTL=300秒）
    await set_cache("categories:list", [CategoryOut.model_validate(c).model_dump() for c in categories], ttl=300)
    return categories
    # if current_user.role != 'admin':
    #     raise HTTPException(status_code=403, detail="只有管理员才能修改分类")
    # result = await db.execute(select(Category).order_by(Category.id.asc()))
    # return result.scalars().all()


@router.put("/categories/{id}", response_model=CategoryOut)
async def update_category(
        id: int,
        category_data: CategoryUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(Category).where(Category.id == id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 只更新传了的字段，不动的保持不变.model_dump() 把 Pydantic 对象转成 Python 字典（{"name": "新分类名"}）
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)
    await delete_cache("categories:list")
    return category


@router.delete("/categories/{id}")
async def delete_category(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["admin"])),
):
    result = await db.execute(select(Category).where(Category.id == id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    await db.delete(category)
    await db.commit()
    await delete_cache("categories:list")
    return {"detail": "删除成功"}
