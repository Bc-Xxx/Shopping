from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth, product, category, cart, order

from app.config import get_settings

from sqlalchemy import text

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Shop",
    description="PostgreSQL 企业级商城学习项目",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(product.router, prefix="/api/v1", tags=["商品"])
app.include_router(category.router, prefix="/api/v1", tags=["分类"])
app.include_router(cart.router, prefix="/api/v1", tags=["购物车"])
app.include_router(order.router, prefix="/api/v1", tags=["订单"])


@app.get("/")
def root():
    return {"message": "Shop API"}


@app.get("/health")
def health():
    return {"status": "ok"}
