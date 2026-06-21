from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import User
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryOut
from ..utils.security import get_current_user

router = APIRouter()


@router.post("/categories", response_model=CategoryOut)
async def create_category(
        category: CategoryCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="只有管理员才能创建分类")
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
    return new_category


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(
        db: AsyncSession = Depends(get_db),
):
    # if current_user.role != 'admin':
    #     raise HTTPException(status_code=403, detail="只有管理员才能修改分类")
    result = await db.execute(select(Category).order_by(Category.id.asc()))
    return result.scalars().all()
