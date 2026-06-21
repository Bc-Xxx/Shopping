import urllib.request, json

BASE = "http://localhost:8012"

# register
data = json.dumps({"username": "alice", "password": "123456"}).encode()
r = urllib.request.Request(f"{BASE}/api/v1/register", data=data,
    headers={"Content-Type": "application/json"}, method="POST")
resp = urllib.request.urlopen(r)
print(f"register: {resp.status} {resp.read().decode()}")

# login with form
r = urllib.request.Request(f"{BASE}/api/v1/login",
    data=b"username=alice&password=123456",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST")
resp = urllib.request.urlopen(r)
body = json.loads(resp.read().decode())
token = body["access_token"]
print(f"login: {resp.status} access_token={token[:20]}...")

# users/me with token
r = urllib.request.Request(f"{BASE}/api/v1/users/me",
    headers={"Authorization": f"Bearer {token}"})
resp = urllib.request.urlopen(r)
print(f"users/me: {resp.status} {resp.read().decode()}")
