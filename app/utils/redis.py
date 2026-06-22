# ① 连接池
import json
import logging
from redis.asyncio import from_url, Redis

from ..config import get_settings

logger = logging.getLogger(__name__)

redis_client: Redis | None = None


# ② 初始化函数（启动时调）
async def init_redis():
    global redis_client
    settings = get_settings()
    try:
        redis_client = await from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis 连接成功")
    except Exception as e:
        redis_client = None
        logger.warning(f"Redis 连接失败，降级为无缓存模式: {e}")


# ③ 四个工具函数
async def get_cache(key: str) -> dict | None:
    if redis_client is None:
        return None
    data = await redis_client.get(key)
    return json.loads(data) if data else None


async def set_cache(key: str, value: dict, ttl: int = 300):
    if redis_client is None:
        return
    await redis_client.setex(key, ttl, json.dumps(value, default=str))


async def delete_cache(key: str):
    if redis_client is None:
        return
    await redis_client.delete(key)


async def clear_cache(pattern: str = "*"):
    if redis_client is None:
        return
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)


# ④ 关闭函数
async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
