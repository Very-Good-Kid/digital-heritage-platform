# 部署指南

## 部署到 Render

### 1. 准备工作

- 项目推送到 GitHub
- 注册 [Render](https://render.com) 账号
- 注册 [Neon](https://neon.tech) 获取免费PostgreSQL

### 2. 创建 Web Service

1. Render Dashboard → "New +" → "Web Service"
2. 连接 GitHub 仓库
3. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120`

### 3. 环境变量

| 变量名 | 值 | 必需 |
|--------|-----|------|
| `FLASK_ENV` | `production` | 是 |
| `SECRET_KEY` | 随机32位+密钥 | 是 |
| `DATABASE_URL` | Neon PostgreSQL连接串 | 是 |
| `ZHIPU_API_KEY` | 智谱AI密钥 | 是 |
| `SILICONFLOW_API_KEY` | SiliconFlow密钥 | 推荐 |
| `TAVILY_API_KEY` | Tavily搜索密钥 | 否 |

### 4. 创建管理员

部署成功后，在Render Shell中运行：
```bash
python scripts/create_admin.py
```

或通过注册页面注册后，在Python REPL中提升权限：
```python
from app import app, db, User
with app.app_context():
    user = User.query.filter_by(username='your_username').first()
    user.is_admin = True
    db.session.commit()
```

---

## 本地开发

```bash
pip install -r requirements.txt
python app.py
# 访问 http://localhost:5000
```

**重要**：本地开发时 `.env` 中不要设置 `DATABASE_URL`，使用本地 SQLite。

---

## 数据库说明

| 环境 | 数据库 | 说明 |
|------|--------|------|
| 本地 | SQLite | `instance/digital_heritage.db`，无需配置 |
| 线上 | Neon PostgreSQL | 免费版5分钟无活动后休眠，首次请求冷启动2-5秒 |

### 知识库同步（本地→云端）

```bash
python scripts/sync_knowledge_to_neon.py           # 执行同步
python scripts/sync_knowledge_to_neon.py --dry-run # 仅预览
```

---

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 部署失败 | 依赖或Python版本 | 检查requirements.txt和runtime.txt |
| 数据库连接失败 | Neon休眠 | 刷新重试，已配置pool_pre_ping |
| 内存不足 | 512MB限制 | 优化查询，减少并发 |
| AI功能不可用 | API密钥未配置 | 设置ZHIPU_API_KEY和SILICONFLOW_API_KEY |
