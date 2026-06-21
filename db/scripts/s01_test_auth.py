import httpx
import asyncio

BASE = "http://localhost:8005"

async def test():
    async with httpx.AsyncClient() as c:
        # 注册
        r = await c.post(f"{BASE}/api/v1/register", json={"username":"alice","password":"123456"})
        print(f"register: {r.status_code} {r.json()}")

        # 模拟 Authorize 发表单登录
        r = await c.post(f"{BASE}/api/v1/login", data={"username":"alice","password":"123456"})
        print(f"login(form): {r.status_code} {r.json()}")

        token = r.json()["access_token"]

        # 用 token 调 users/me
        r = await c.get(f"{BASE}/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        print(f"users/me: {r.status_code} {r.json()}")

        # 文章列表
        r = await c.get(f"{BASE}/api/v1/users?skip=0&limit=10")
        print(f"users: {r.status_code} {r.json()}")

asyncio.run(test())
