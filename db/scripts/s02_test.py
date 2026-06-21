import httpx, asyncio

BASE = "http://127.0.0.1:8001/api/v1"

async def test():
    async with httpx.AsyncClient() as c:
        # 创建分类
        r = await c.post(f"{BASE}/categories", json={"name": "科技"})
        print(f"创建科技: {r.status_code} {r.json()}")

        r = await c.post(f"{BASE}/categories", json={"name": "编程", "parent_id": 1})
        print(f"创建编程: {r.status_code} {r.json()}")

        r = await c.post(f"{BASE}/categories", json={"name": "文学"})
        print(f"创建文学: {r.status_code} {r.json()}")

        # 分类列表
        r = await c.get(f"{BASE}/categories")
        print(f"\n分类列表: {r.status_code} {r.json()}")

        # 注册用户
        r = await c.post(f"{BASE}/register", json={"username": "alice", "password": "123456"})
        print(f"\n注册: {r.status_code} {r.json()}")

        # 登录
        r = await c.post(f"{BASE}/login", data={"username": "alice", "password": "123456"})
        print(f"登录: {r.status_code}")
        token = r.json().get("access_token", "")

        # 创建文章
        r = await c.post(
            f"{BASE}/articles",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "PostgreSQL入门",
                "content": "这是一篇关于PG的文章",
                "category_id": 2,
                "tags": ["SQL", "新手"]
            },
        )
        print(f"创建文章: {r.status_code} {r.json()}")

        # 文章列表（带分页总数）
        r = await c.get(f"{BASE}/articles?skip=0&limit=10")
        print(f"\n文章列表: {r.status_code} {r.json()}")

asyncio.run(test())
