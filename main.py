import time

from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import auth, product, category, cart, order

from app.config import get_settings
from app.utils.logger import setup_logging, get_logger
from app.utils.redis import init_redis, close_redis

settings = get_settings()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("日志系统已初始化")
    await init_redis()  # 加载缓存
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_redis()  # 关闭缓存
    await engine.dispose()


app = FastAPI(
    title="Shop",
    description="PostgreSQL 企业级商城学习项目",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许哪些前端域名访问，上线后换成生产域名
    allow_credentials=True,  # 允许携带 cookie
    allow_methods=["*"],  # 允许的 HTTP 方法，* 表示全部
    allow_headers=["*"],  # 允许的自定义请求头，* 表示全部
)


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
    request.state.trace_id = trace_id

    start = time.time()
    response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)

    logger.info(
        f"{request.method} {request.url.path} | {response.status_code} | {elapsed_ms}ms | {trace_id}"
    )

    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未捕获异常 | {request.method} {request.url.path} | {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
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
