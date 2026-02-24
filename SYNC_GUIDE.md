# 数据同步使用指南

## 问题描述

- **本地开发环境**: 使用 SQLite 数据库
- **Render 部署环境**: 使用 Neon PostgreSQL 数据库
- 两个数据库独立，需要手动同步数据

## 解决方案

通过Web界面同步FAQ数据（推荐方式）

### 步骤1: 部署到Render

1. 将代码推送到GitHub
2. Render会自动部署
3. 部署完成后，访问你的应用

### 步骤2: 访问数据同步页面

1. 登录管理员账户
2. 访问: `https://你的应用名.onrender.com/admin/sync`

### 步骤3: 执行同步

1. 点击"同步FAQ数据"按钮
2. 等待同步完成
3. 查看同步结果

### 步骤4: 验证数据

访问 `https://你的应用名.onrender.com/faq` 查看FAQ数据是否已同步

## 注意事项

1. **管理员权限**: 只有管理员账户可以访问数据同步功能
2. **数据覆盖**: 同步会覆盖相同ID的FAQ记录
3. **网络要求**: 需要能访问Render应用的网络环境
4. **CSRF保护**: 同步端点已配置CSRF保护

## 本地数据管理

### 导出FAQ数据

```bash
python sync_faq.py
```

这将导出FAQ数据到JSON文件。

### 查看本地FAQ

```bash
python -c "
from app import app
from models import FAQ
with app.app_context():
    faqs = FAQ.query.all()
    print(f'本地FAQ数量: {len(faqs)}')
    for faq in faqs:
        print(f'ID: {faq.id}, 分类: {faq.category}, 问题: {faq.question[:30]}...')
"
```

## 更新同步数据

如果需要更新同步的FAQ数据：

1. 在本地修改FAQ数据（通过后台管理或直接操作数据库）
2. 更新 `admin/views.py` 中的 `FAQ_DATA` 列表
3. 重新部署到Render
4. 访问 `/admin/sync` 页面执行同步

## 常见问题

### Q: 为什么需要手动同步？

A: 本地开发使用SQLite，生产环境使用PostgreSQL，两者是独立的数据库。为了避免意外覆盖生产数据，默认不会自动同步。

### Q: 同步会删除现有数据吗？

A: 不会删除现有数据，只会新增或更新相同ID的FAQ记录。

### Q: 如何确保数据安全？

A: 建议在同步前：
1. 备份生产环境数据库
2. 在测试环境先验证
3. 确认数据正确后再执行同步

### Q: 可以同步其他数据吗？

A: 目前只支持FAQ数据同步。如需同步其他数据（用户、资产、遗嘱等），需要额外开发对应的同步端点。
