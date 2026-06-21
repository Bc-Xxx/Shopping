import sys, os; sys.path.insert(0, os.getcwd())
import httpx, asyncio, sqlalchemy as sa
from main import app
from httpx import ASGITransport
from app.database import engine

BASE = '/api/v1'

async def test():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as c:
        # 1. 创建分类
        r = await c.post(f'{BASE}/categories', json={'name': 'Electronics'})
        cat1 = r.json()['id']
        print(f'category created: id={cat1}')

        # 2. 注册买家
        r = await c.post(f'{BASE}/register', json={'username': 'buyer1', 'password': '123456'})
        print(f'register buyer1: {r.json()}')
        r = await c.post(f'{BASE}/login', data={'username': 'buyer1', 'password': '123456'})
        token_buyer = r.json()['access_token']

        # 3. 买家创建商品 → 403
        r = await c.post(f'{BASE}/products',
            headers={'Authorization': f'Bearer {token_buyer}'},
            json={'name': 'MacBook', 'description': 'test', 'category_id': cat1, 'tags': ['laptop']})
        print(f'buyer create: {r.status_code}', r.json())

        # 4. 数据库改 role 为 seller
        async with engine.begin() as conn:
            await conn.execute(sa.text("UPDATE users SET role = 'seller' WHERE username = 'buyer1'"))
            await conn.commit()
        print('role updated to seller')

        # 5. seller 创建商品 → 200
        r = await c.post(f'{BASE}/products',
            headers={'Authorization': f'Bearer {token_buyer}'},
            json={'name': 'MacBook Pro', 'description': 'Apple laptop', 'category_id': cat1, 'tags': ['Apple', 'Laptop']})
        print(f'seller create: {r.status_code}', r.json())

        # 6. 注册另一个买家
        r = await c.post(f'{BASE}/register', json={'username': 'buyer2', 'password': '123456'})
        r = await c.post(f'{BASE}/login', data={'username': 'buyer2', 'password': '123456'})
        token_b2 = r.json()['access_token']
        r = await c.post(f'{BASE}/products',
            headers={'Authorization': f'Bearer {token_b2}'},
            json={'name': 'iPhone', 'description': 'test', 'category_id': cat1, 'tags': ['phone']})
        print(f'buyer2 create: {r.status_code}', r.json())

        # 7. 公开浏览商品
        r = await c.get(f'{BASE}/products')
        print(f'public list: {r.status_code}, total={r.json()["total"]}')

        # 8. 查看用户列表（确认 role 字段）
        r = await c.get(f'{BASE}/users')
        for u in r.json():
            print(f'  user: {u["username"]}, role={u["role"]}')

asyncio.run(test())
