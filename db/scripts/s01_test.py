import httpx, asyncio, sys
BASE = "http://localhost:8006"

async def test():
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE}/api/v1/register", json={"username":"alice","password":"123456"})
        print(f"reg: {r.status_code} {r.text}")
        r = await c.post(f"{BASE}/api/v1/login", data={"username":"alice","password":"123456"})
        print(f"login: {r.status_code} {r.text}")
        if r.status_code == 200:
            token = r.json()["access_token"]
            r = await c.get(f"{BASE}/api/v1/users/me", headers={"Authorization":f"Bearer {token}"})
            print(f"me: {r.status_code} {r.text}")

asyncio.run(test())
