# Shop — PostgreSQL 企业级学习计划

## 个人信息

- **学习方式**: 项目驱动（纯商城系统）
- **时间投入**: 每日 3 小时+
- **角色**: 纯后端
- **交互模式**: 你写代码 → 我 review + 讲数据库原理
- **代码风格**: 中期 ORM（SQLAlchemy asyncio）→ 后期原生 SQL 深入
- **现有基础**: 能写简单 CRUD SQL，有 FastAPI 基础

---

## 项目演进总览

```
Sprint 1 ──→ 用户注册登录（建表/CRUD/约束/数据类型/角色权限）
  │
Sprint 2 ──→ 商品与分类系统（外键/自引用/数组/JOIN/窗口函数分页）
  │
Sprint 3 ──→ 商品扩展与搜索（JSONB/GIN全文检索/复合索引）
  │
Sprint 4 ──→ 购物车与订单（事务/ACID/行级锁）
  │
Sprint 5 ──→ 销售报表（聚合/GROUP BY/窗口函数）
  │ 
Sprint 6 ──→ 库存秒杀（MVCC/隔离级别/乐观锁vs悲观锁）
  │
Sprint 7 ──→ 大表归档（表分区/数据迁移）
  │
Sprint 8 ──→ 生产部署（备份/权限/连接池/监控）
```

---

## 分 Sprint 知识点清单

### Sprint 1 — 用户系统

| 模块 | API | 数据库知识点 |
|------|-----|------------|
| 用户注册 | `POST /register` | `CREATE TABLE`、数据类型、`SERIAL` 自增、`UNIQUE` 约束、`NOT NULL`、`DEFAULT`、`INSERT ... RETURNING` |
| 用户登录 | `POST /login` | `SELECT` 条件查询、参数化查询防注入、密码哈希存储 |
| 个人信息 | `GET /users/me` | `SELECT WHERE PK`、`LIMIT 1` |
| 用户列表 | `GET /users` | `ORDER BY`、`LIMIT/OFFSET` 分页 |
| 角色权限 | 商品/分类接口校验 | `CHECK` 约束模拟枚举、`VARCHAR` 类型、`DEFAULT` |
| 建表初始化 | — | `CREATE DATABASE`、`\dt`、`\d` 查看表结构 |

**涉及的 PostgreSQL 数据类型**:
- `SERIAL` — 自增整数主键
- `VARCHAR(n)` — 定长字符串
- `TEXT` — 不限长字符串
- `TIMESTAMP WITH TIME ZONE` — 带时区时间戳
- `BOOLEAN` — 布尔值

### Sprint 2 — 商品系统 + 分类管理

| 模块 | 数据库知识点 |
|------|------------|
| 分类管理 | `FOREIGN KEY`、自引用外键（无限级分类树） |
| 商品 CRUD | `ON DELETE RESTRICT`、级联策略 |
| 标签系统 | PostgreSQL `TEXT[]` 数组类型 |
| 商品列表 | 多表 `LEFT JOIN`、`COUNT(*) OVER()` 窗口函数分页 |

### Sprint 3 — 商品扩展与搜索

| 模块 | 数据库知识点 |
|------|------------|
| 商品扩展属性 | `JSONB` 存储、`CHECK` 约束 |
| 分类树查询 | 递归 CTE `WITH RECURSIVE` |
| 全文搜索 | `GIN` 索引、`tsvector`/`tsquery`、`LIKE`/`ILIKE` |
| 搜索排序 | 复合索引、`ORDER BY` 与索引的关系 |

### Sprint 4 — 购物车与订单

| 模块 | 数据库知识点 |
|------|------------|
| 购物车 | 唯一复合约束（user_id + product_id） |
| 下单 | 事务 `BEGIN/COMMIT/ROLLBACK`、ACID |
| 库存扣减 | `SELECT ... FOR UPDATE` 行级锁 |
| 订单状态机 | `CHECK` 约束模拟枚举、状态变更 |

### Sprint 5 — 报表与数据分析

| 模块 | 数据库知识点 |
|------|------------|
| 销售汇总 | `COUNT/SUM/AVG`、`GROUP BY`、`HAVING` |
| 排名分析 | `ROW_NUMBER()`、`RANK()`、`DENSE_RANK()` |
| 环比同比 | `LAG()`/`LEAD()` 窗口函数 |
| 累计统计 | 窗口帧 `ROWS BETWEEN` |

### Sprint 6 — 库存秒杀

| 模块 | 数据库知识点 |
|------|------------|
| 秒杀接口 | MVCC 原理、事务隔离级别 |
| 超卖解决 | 乐观锁（版本号 `UPDATE ... WHERE version =`） |
| 超卖解决 | 悲观锁（`SELECT ... FOR UPDATE NOWAIT`） |
| 并发验证 | `SERIALIZABLE` 隔离级别、重试机制 |

### Sprint 7 — 数据大表归档

| 模块 | 数据库知识点 |
|------|------------|
| 订单归档 | 表分区 `PARTITION BY RANGE` |
| 商品分区 | `PARTITION BY LIST`（按类别） |
| 历史数据 | `ATTACH/DETACH PARTITION`、数据迁移 |
| 查询优化 | 分区裁剪、`EXPLAIN` 验证 |

### Sprint 8 — 生产部署

| 模块 | 数据库知识点 |
|------|------------|
| 备份恢复 | `pg_dump`、`pg_restore`、定时备份脚本 |
| 权限管理 | `CREATE ROLE`、`GRANT`、行级安全（RLS） |
| 连接池 | PgBouncer 概念、`psycopg2.pool` |
| 监控 | `pg_stat_activity`、慢查询日志、`pg_stat_statements` |

---

## 当前项目结构

```
pg/
├── main.py                     # FastAPI 入口
├── app/
│   ├── config.py               # 配置（DB连接、JWT密钥）
│   ├── database.py             # SQLAlchemy 异步引擎 + FatherBase
│   ├── models/
│   │   ├── user.py             # 用户模型（含 role CHECK 约束）
│   │   ├── product.py          # 商品模型（含 tags TEXT[]）
│   │   ├── category.py         # 分类模型（自引用外键树）
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py             # 注册/登录/用户输出
│   │   ├── product.py          # 商品CRUD + 分页响应
│   │   └── category.py         # 分类CRUD
│   ├── routers/
│   │   ├── auth.py             # 注册/登录/用户列表
│   │   ├── product.py          # 商品增删改查（仅 seller）
│   │   └── category.py         # 分类增删查（仅 admin）
│   └── utils/
│       └── security.py         # bcrypt密码 + JWT令牌
├── db/
│   ├── SCHEMA_EVOLUTION.md     # 数据库 Schema 演进
│   ├── scripts/                # 测试脚本
│   └── Sprint1_TASKS.md
├── alembic/                    # 数据库迁移（尚未使用）
└── requirements.txt
```

## 当前数据表关系

```
users                           categories
 ├── id (PK)                     ├── id (PK)
 ├── username (UNIQUE)           ├── name (UNIQUE)
 ├── hash_password               ├── parent_id → categories.id
 ├── role (buyer/seller/admin)   ├── created_at
 ├── created_at                  └── updated_at
 └── updated_at
        │                              │
        │                      ┌───────┘
        │                      │
        │     products
        │      ├── id (PK)
        └──────┼── seller_id → users.id
               ├── name
               ├── description
               ├── category_id → categories.id (ON DELETE RESTRICT)
               ├── tags TEXT[]
               ├── created_at
               └── updated_at
```

---

## 进度跟踪

| Sprint | 状态 | 完成日期 |
|--------|------|---------|
| 1 — 用户系统 | ✅ | |
| 2 — 商品与分类 | ✅ | |
| 3 — 商品扩展与搜索 | ⬜ | |
| 4 — 购物车与订单 | ⬜ | |
| 5 — 报表分析 | ⬜ | |
| 6 — 库存秒杀 | ⬜ | |
| 7 — 大表归档 | ⬜ | |
| 8 — 生产部署 | ⬜ | |
