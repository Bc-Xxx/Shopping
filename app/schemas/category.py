from datetime import datetime

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    # 前端传什么？
    name: str         # 分类名，必填
    parent_id: int | None = None  # 父分类 ID，不传就是顶层分类

class CategoryOut(BaseModel):
    # API 返回什么？
    id: int
    name: str
    parent_id: int | None = None
    created_at: datetime            # 从 FatherBase 继承来的
    updated_at: datetime | None = None

    class Config:
        from_attributes = True      # 告诉 Pydantic 可以从 ORM 对象读取