from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserOut
from ..utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册
    步骤：
      1. 查重：查询 username 是否已存在
      2. 创建 User 实例，password 用 hash_password() 加密
      3. db.add + await db.commit + await db.refresh
      4. 返回 user
    """
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:  # ✅ 现在这是真正的 User 对象或者 None
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(
        username=user_data.username,
        hash_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hash_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(data={"id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    直接返回 current_user（get_current_user 已做全部工作）
    """
    return current_user


@router.get("/users", response_model=list[UserOut])
async def list_users(
        skip: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()
