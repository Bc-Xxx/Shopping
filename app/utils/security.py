import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import get_settings
from ..database import get_db
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
settings = get_settings()


def hash_password(password: str) -> str:
    """
    接收明文密码，返回 bcrypt 哈希值
    提示：bcrypt.hashpw(密码.encode(), bcrypt.gensalt()).decode()
    """
    hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hash.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否匹配存储的哈希值
    提示：bcrypt.checkpw(明文.encode(), 哈希.encode())
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict) -> str:
    """
    生成 JWT token
    data: 要编码的数据（如 {"id": 1}）
    需要把 data 复制一份，加上 exp 过期字段，再用 jwt.encode()
    过期时间 = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    """
    new_data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    new_data.update({"exp": expire})
    return jwt.encode(new_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """
    验证 JWT token，成功返回 payload dict，失败返回 None
    提示：jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
) -> User:
    """
    从请求中提取 token → 解析 → 查数据库 → 返回当前用户
    步骤：
      1. payload = verify_token(token)
      2. payload 是 None → 抛 HTTPException(401, "无效的 token")
      3. result = await db.execute(select(User).where(User.id == payload["id"]))
      4. user = result.scalar_one_or_none()
      5. user 是 None → 抛 HTTPException(401, "用户不存在")
      6. return user
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的 token")
    result = await db.execute(select(User).where(User.id == payload["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


# 验证是不是admin
def require_roles(allowed_roles: list[str]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="权限不足")
        return current_user

    return role_checker
