# 扩展学习：日志 + 中间件 + Redis 缓存

> 本计划与 Sprint 1~8 独立，不冲突。随时可切回主计划。

## 学习目标

在现有商城项目上加入生产环境必备的三层基础设施：

```
请求进来
  │
  ├── 第一阶段：日志系统 + 中间件（合并）
  │     ├── 日志系统（Logger / Handler / Formatter / Filter）
  │     └── 中间件（RequestID / ProcessTime / AccessLog / ErrorHandler）
  │
  ├── 第二阶段：Redis 缓存（加速查询）
  │     ├── 连接池 + Cache Aside 模式
  │     └── 分类 / 商品接口缓存
  │
  └── 路由处理 → 数据库
```

---

## 第一阶段：日志系统 + 中间件（合并）

> 日志是基础设施的基石，中间件依赖日志输出访问记录，
> 且 RequestContextFilter 需要中间件生成的 request_id 才能工作，
> 合并在一起做逻辑最顺。

### 子阶段 A：日志基础设施

#### 知识点

| 概念 | 说明 |
|------|------|
| `logging.getLogger(name)` | 获取 logger，按模块名分层 |
| `Handler` | 输出到哪：控制台 / 文件 / 网络 |
| `Formatter` | 输出格式：纯文本 / JSON |
| `Filter` | 给日志行附加数据（如 request_id） |
| `RotatingFileHandler` | 文件按大小/时间轮转 |

#### 步骤

| # | 内容 | 文件 |
|---|------|------|
| A1 | 理解 logging 四件套：Logger / Level / Handler / Formatter | 理论 |
| A2 | `config.py` + `.env` 加 `LOG_LEVEL` / `LOG_FILE` | ✏️ 修改 |
| A3 | 创建 `app/utils/logger.py`：控制台 + 文件双输出，JSON 格式 | ✨ 新增 |
| A4 | `main.py` lifespan 调 `setup_logging()` | ✏️ 修改 |
| A5 | 把所有 `print()` 和裸 `raise` 改成 logging | ✏️ 修改 |

### 子阶段 B：中间件

#### 知识点

| 概念 | 说明 |
|------|------|
| 中间件洋葱圈 | 请求从外到内，响应从内到外 |
| `request.state` | 在中间件和路由之间传数据 |
| `call_next(request)` | 调用下一个中间件或路由 |
| 中间件注册顺序 | 先注册的在外层 |

#### 步骤

| # | 内容 | 文件 |
|---|------|------|
| B1 | 理解 FastAPI 中间件机制（洋葱模型） | 理论 |
| B2 | **RequestID 中间件**：生成 uuid，注入 `request.state`，加响应头 | `main.py` |
| B3 | **ProcessTime 中间件**：记录耗时，加 `X-Process-Time` 头 | `main.py` |
| B4 | **AccessLog 中间件**：复用日志输出结构化访问日志 | `main.py` |
| B5 | **ErrorHandler 中间件**：兜底异常，统一 JSON（不暴露 traceback） | `main.py` |
| B6 | **RequestContextFilter 上线**：消费 `request.state.request_id`，注入日志 | `logger.py` |
| B7 | 跑通全链路验证洋葱模型顺序 | 验证 |

---

## 第二阶段：Redis 缓存

### 子阶段 A：基础设施

#### 知识点

| 概念 | 说明 |
|------|------|
| 连接池 | 复用连接，避免每次建连 |
| 优雅降级 | Redis 挂了不崩服务，直接查 DB |
| 序列化 | Python dict ↔ JSON string ↔ Redis string |

#### 步骤

| # | 内容 | 文件 |
|---|------|------|
| A1 | 理解 Redis 核心命令 `SET/GET/DEL/EXPIRE/KEYS` + Docker 启动 | 理论 |
| A2 | `config.py` + `.env` 加 `REDIS_URL` | ✏️ 修改 |
| A3 | 创建 `app/utils/redis.py`：连接池 + get/set/delete/clear | ✨ 新增 |
| A4 | `main.py` lifespan 集成 Redis（启动连、关闭断） | ✏️ 修改 |
| A5 | `requirements.txt` + `redis` | ✏️ 修改 |

### 子阶段 B：缓存业务

#### 知识点

| 概念 | 说明 |
|------|------|
| Cache Aside 模式 | 读→cache miss→查DB→写回cache |
| TTL | 过期时间，防止脏数据永久存在 |
| 缓存失效 | 数据变更时主动删除/更新缓存 |

#### 步骤

| # | 内容 | 文件 |
|---|------|------|
| B1 | 分类列表加缓存（最简单的只读数据） | `category.py` |
| B2 | 商品列表/详情/搜索加缓存 | `product.py` |
| B3 | 商品增删改时主动清除相关缓存 | `product.py` |
| B4 | 测试缓存命中/未命中 + Redis 断开时降级 | 验证 |

---

## 预期新增/修改文件总览

```
✨ 新增 2 个文件：
  app/utils/logger.py    — 日志配置
  app/utils/redis.py     — Redis 连接池 + 缓存工具

✏️ 修改 6 个文件：
  app/config.py           — 增加 REDIS_URL / LOG_LEVEL / LOG_FILE
  .env                    — 增加环境变量
  main.py                 — 生命周期 + 中间件 + 日志初始化
  app/routers/product.py  — 商品接口加缓存 + print→logging
  app/routers/category.py — 分类接口加缓存 + print→logging
  requirements.txt        — +redis

💡 不改的（原因）：
  auth/cart/order router  — 用户/订单是私有数据，不适合缓存
  models/schemas          — 数据层无变动
  database.py             — 数据库连接层无变动
```

---

## 两阶段完成后的能力

| 阶段 | 你能回答什么 |
|------|------------|
| 日志+中间件 | logging 四件套、Handler 组合、结构化日志、RequestContextFilter、洋葱模型、request.state、中间件顺序、异常处理 |
| Redis | 连接池、Cache Aside、TTL、缓存失效、优雅降级 |

面试话术示例：
> "我在项目里引入了 Redis 缓存分类和商品列表，采用 Cache Aside 模式，更新商品时主动失效缓存，Redis 异常时降级查 DB 不中断服务。中间件层实现了请求 ID 追踪、耗时统计和结构化访问日志。"

---

## 开始条件

- [ ] 已安装 Redis（本地或 Docker）
- [ ] 当前 Sprint 4 代码已提交
