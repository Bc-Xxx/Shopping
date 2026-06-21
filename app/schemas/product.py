from datetime import datetime
from typing import List, Any

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    category_id: int
    tags: list[str] = []
    price: float
    stock: int
    attrs: dict[str, Any] = {}


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    seller_id: int
    created_at: datetime
    updated_at: datetime | None = None
    category_id: int
    category_name: str | None = None
    tags: list[str] = []
    price: float
    stock: int
    attrs: dict[str, Any] = {}

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    tags: list[str] | None = None
    price: float | None = None
    stock: int | None = None
    attrs: dict[str, Any] | None = None


class PaginatedProducts(BaseModel):
    total: int
    items: list[ProductOut]


class SearchResult(BaseModel):
    total: int
    items: list[ProductOut]
