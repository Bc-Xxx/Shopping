# Sprint 1 — 用户系统：你的任务清单

## 总览

你要填 2 个文件，一共 8 个函数。每个函数都标注了 `# TODO`。

---

## 文件 1：`app/utils/security.py`（5 个函数）

### 1. `hash_password(password: str) -> str`
```
bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
```

### 2. `verify_password(plain_password: str, hashed_password: str) -> bool`
```
bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

### 3. `create_access_token(data: dict) -> str`
用 `jwt.encode()` 生成 token，包含：
- `data` 中的字段（如 `{"id": 1}`）
- `exp` 过期时间（当前时间 + settings.JWT_EXPIRE_MINUTES）
- 算法用 `settings.JWT_ALGORITHM`
- 密钥用 `settings.JWT_SECRET_KEY`

### 4. `verify_token(token: str) -> dict | None`
用 `jwt.decode()` 解析 token，失败返回 None

### 5. `get_current_user(token, db) -> User`
1. 调 `verify_token(token)` 解析 token
2. 失败 → 抛 401
3. 成功 → `await db.execute(select(User).where(User.id == payload["id"]))`
4. 查不到 → 抛 401
5. 返回 user

---

## 文件 2：`app/routers/auth.py`（4 个函数）

### 1. `POST /register`
```
1. 查重：查询 username 是否已存在
2. 创建 User 对象，password 用 hash_password() 加密
3. db.add + await db.commit + await db.refresh
4. 返回 user
```

### 2. `POST /login`
```
1. 按 username 查用户
2. 不存在或密码不匹配 → 抛 401
3. 调 create_access_token(data={"id": user.id}) 生成 token
4. 返回 TokenOut(token=token)
```

### 3. `GET /users/me`
```
直接返回 current_user（由 get_current_user 注入）
```

### 4. `GET /users`
```
SELECT User，按 created_at 倒序，offset(skip).limit(limit)
```

---

## 验证方法

```bash
# 启动
uvicorn main:app --reload

# 测试（用 test_main.http 或 curl）
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"123456"}'
```
