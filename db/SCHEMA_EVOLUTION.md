# Shop 数据库 Schema 演进

```
Sprint 1                          Sprint 2
┌───────────────┐                 ┌──────────────────┐
│     users     │                 │    products      │
├───────────────┤                 ├──────────────────┤
│ id (PK)       │                 │ id (PK)          │
│ username      │                 │ name             │
│ hash_password │                 │ description      │
│ role          │── CHECK         │ seller_id (FK) ──┤
│ avatar        │  buyer/seller   │ category_id (FK) │──┐
│ is_active     │  /admin         │ tags TEXT[]      │  │
│ created_at    │                 │ created_at       │  │
│ updated_at    │                 │ updated_at       │  │
└───────┬───────┘                 └──────────────────┘  │
        │                                               │
        │              ┌──────────────────────┐          │
        │              │     categories       │          │
        │              ├──────────────────────┤          │
        └──────────────┤ id (PK)              │          │
                       │ name (UNIQUE)        │          │
                       │ parent_id (self-ref) │──────────┘
                       │ created_at           │
                       │ updated_at           │
                       └──────────────────────┘

Sprint 3                          Sprint 4
┌───────────┐                    ┌───────────┐  ┌──────────────┐
│ products  │ (+attrs JSONB)     │   carts   │  │   orders     │
│ (+price)  │                    ├───────────┤  ├──────────────┤
│ (+stock)  │                    │ id (PK)   │  │ id (PK)      │
│ (+search_vector)               │ user_id   │  │ user_id      │
│ (+GIN idx)│                    │ product_id│  │ total_amount │
└───────────┘                    │ quantity  │  │ status       │
                                 │ UNIQUE(u+p)│ │ created_at   │
                                 └───────────┘  └──────────────┘
                                                       │
                                              ┌────────┘
                                              │
                                   ┌──────────────────┐
                                   │   order_items    │
                                   ├──────────────────┤
                                   │ order_id (FK)    │
                                   │ product_id (FK)  │
                                   │ quantity         │
                                   │ unit_price       │
                                   └──────────────────┘

Sprint 5-7  以上表增加索引/分区/触发器
Sprint 8    增加角色/权限/备份配置
```

## 新增字段/变化记录

| Sprint | 表 | 变更 |
|--------|------|------|
| 2 | products | `category_id` (FK)、`tags` (TEXT[]) |
| 2 | users | `role` + CHECK 约束 |
| 3 | products | `price DECIMAL(10,2)`、`stock INT`、`attrs JSONB`、`search_vector tsvector`、`ix_products_search_vector GIN` |
| 3 | — | `GET /products/search?q=` — tsvector/tsquery 全文搜索 + ts_rank 排序 |
| 4 | orders | `version INTEGER`（乐观锁） |
| 6 | products | `version INTEGER`（乐观锁用） |
| 7 | orders | 转为分区表 `PARTITION BY RANGE(created_at)` |
