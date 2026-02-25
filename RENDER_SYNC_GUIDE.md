# Render 部署与数据库同步指南

## 问题说明

1. **管理员后台 Internal Server Error**：已修复
   - 修复了 `admin/stats.py` 中的重复代码
   - 添加了错误处理，避免数据库查询失败导致页面崩溃
   - 优化了 PostgreSQL 兼容性

2. **数据库同步策略**：仅同步公益普法问答(FAQ)部分
   - Render 上使用 Neon PostgreSQL 数据库
   - 本地使用 SQLite 数据库
   - 只同步 FAQ 表，其他表不同步

## 数据库配置

### 本地开发环境
- 数据库类型：SQLite
- 数据库路径：`instance/digital_heritage.db`
- 配置文件：`config.py` (DevelopmentConfig)

### Render 生产环境
- 数据库类型：PostgreSQL (Neon)
- 连接字符串：通过环境变量 `DATABASE_URL` 配置
- 配置文件：`config.py` (ProductionConfig)

## 同步策略

### 仅同步 FAQ 数据

**原则**：
- ✅ 同步：FAQ 表（公益普法问答）
- ❌ 不同步：User、DigitalAsset、DigitalWill、PlatformPolicy、Story 等表

**原因**：
1. 用户数据（User）涉及隐私，不应在生产环境和开发环境之间同步
2. 资产数据（DigitalAsset、DigitalWill）是用户的个人数据
3. 平台政策（PlatformPolicy）和故事（Story）可能在不同环境有不同的内容
4. FAQ 是公开内容，可以安全地在两个环境之间同步

## 同步步骤

### 方法 1：使用 sync_faq_to_neon.py 脚本（推荐）

```bash
# 确保已设置 DATABASE_URL 环变量（Neon数据库连接字符串）
# 在 .env 文件中配置：
DATABASE_URL=postgresql://neondb_owner:npg_KawHXBLE6GQ5@ep-patient-night-aigubbnd-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# 运行同步脚本
python sync_faq_to_neon.py
```

### 方法 2：手动同步

```python
# 从本地 SQLite 导出 FAQ 数据
import sqlite3
import json

conn = sqlite3.connect('instance/digital_heritage.db')
cursor = conn.cursor()
cursor.execute("SELECT id, question, answer, category, \"order\" FROM faqs")
faqs = cursor.fetchall()

# 导出为 JSON
faq_data = [
    {
        'id': row[0],
        'question': row[1],
        'answer': row[2],
        'category': row[3],
        'order': row[4]
    }
    for row in faqs
]

with open('faq_export.json', 'w', encoding='utf-8') as f:
    json.dump(faq_data, f, ensure_ascii=False, indent=2)

conn.close()
```

然后在 Render 上导入：
```python
# 在 Render 上执行（通过 Python Shell 或脚本）
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.environ.get('DATABASE_URL'))

with open('faq_export.json', 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

with engine.connect() as conn:
    for faq in faq_data:
        # 检查是否存在
        existing = conn.execute(
            text("SELECT id FROM faqs WHERE id = :id"),
            {'id': faq['id']}
        ).fetchone()

        if existing:
            # 更新
            conn.execute(text("""
                UPDATE faqs
                SET question = :question, answer = :answer, category = :category, "order" = :order
                WHERE id = :id
            """), faq)
        else:
            # 插入
            conn.execute(text("""
                INSERT INTO faqs (id, question, answer, category, "order")
                VALUES (:id, :question, :answer, :category, :order)
            """), faq)

    conn.commit()
```

## 部署检查清单

### 本地开发
- [ ] 确保 `instance/digital_heritage.db` 存在
- [ ] 确保本地管理员账号正常
- [ ] 测试本地管理员后台功能

### Render 部署
- [ ] 设置环境变量：
  - `DATABASE_URL`：Neon PostgreSQL 连接字符串
  - `SECRET_KEY`：随机生成的密钥
  - `FLASK_ENV=production`
- [ ] 初始化数据库表（首次部署）
- [ ] 创建管理员账号（首次部署）
- [ ] 同步 FAQ 数据到 Neon

### FAQ 同步
- [ ] 从本地导出 FAQ 数据
- [ ] 同步到 Render 的 Neon 数据库
- [ ] 验证 Render 上的 FAQ 数据是否正确

## 常见问题

### 1. 管理员后台显示 Internal Server Error

**已修复**：`admin/stats.py` 中的重复代码已被删除，并添加了错误处理。

### 2. 连接 Neon 数据库失败

检查：
- `DATABASE_URL` 环境变量是否正确设置
- 连接字符串格式是否正确（postgres:// 应替换为 postgresql://）
- 网络连接是否正常

### 3. FAQ 数据同步失败

检查：
- 本地 SQLite 数据库中是否有 FAQ 数据
- Neon 数据库是否已创建 faqs 表
- 数据格式是否一致

### 4. 如何只同步 FAQ 而不同步其他数据？

使用 `sync_faq_to_neon.py` 脚本，该脚本只同步 FAQ 表。不要使用其他同步脚本（如 `sync_to_neon.py`），因为它们可能同步其他表。

## 脚本说明

### sync_faq_to_neon.py
- **用途**：仅同步 FAQ 数据
- **来源**：本地 SQLite
- **目标**：Neon PostgreSQL
- **推荐使用**：✅

### sync_to_neon.py
- **用途**：同步所有数据
- **来源**：本地 SQLite
- **目标**：Neon PostgreSQL
- **推荐使用**：❌（会同步用户等敏感数据）

## 维护建议

1. **定期同步 FAQ**：当本地更新 FAQ 后，及时同步到 Render
2. **保护用户隐私**：不要同步用户数据
3. **测试环境隔离**：开发和生产环境的数据应保持独立
4. **备份重要数据**：定期备份 Neon 数据库

## 联系支持

如有问题，请检查：
1. Render 日志
2. Neon 数据库状态
3. 环境变量配置
4. 脚本执行日志
