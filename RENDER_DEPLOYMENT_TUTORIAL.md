# 🚀 数字遗产继承平台 - Render 详细部署教程

## 📋 目录

1. [前置准备](#前置准备)
2. [方式一：通过 Git 仓库部署（推荐）](#方式一通过-git-仓库部署推荐)
3. [方式二：通过 Docker 部署](#方式二通过-docker-部署)
4. [数据库配置](#数据库配置)
5. [环境变量配置](#环境变量配置)
6. [部署验证](#部署验证)
7. [故障排除](#故障排除)
8. [常见问题 FAQ](#常见问题-faq)

---

## 前置准备

### 1. 必需账号

- ✅ **Render 账号**：[https://render.com](https://render.com)（免费注册）
- ✅ **GitHub 账号**：用于代码托管（可选，但推荐）
- ✅ **Supabase 账号**：用于 PostgreSQL 数据库（推荐，免费）

### 2. 本地工具准备

```bash
# 检查 Git 版本
git --version

# 检查 Python 版本（需要 3.10+）
python --version
```

### 3. 项目文件检查

确保以下文件存在于项目根目录：

```
digital-heritage-platform/
├── app.py                    # 主应用文件
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── runtime.txt              # Python 版本
├── Procfile                 # 启动命令
├── render.yaml              # Render 配置
├── Dockerfile               # Docker 配置
├── utils/
│   ├── fonts.py             # 字体管理（中文字体支持）
│   └── pdf_generator.py     # PDF 生成
├── models.py                # 数据模型
├── templates/               # HTML 模板
├── static/                  # 静态文件
└── instance/                # 本地数据库（开发用）
```

---

## 方式一：通过 Git 仓库部署（推荐）

### 步骤 1：初始化 Git 仓库

```bash
# 进入项目目录
cd "c:\Users\admin\Desktop\demo - codebuddy"

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: Digital Heritage Platform with Chinese font support"
```

### 步骤 2：推送到 GitHub

#### 2.1 创建 GitHub 仓库

1. 访问 [https://github.com/new](https://github.com/new)
2. 输入仓库名称：`digital-heritage-platform`
3. 选择 **Public** 或 **Private**
4. 点击 **Create repository**

#### 2.2 推送代码

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/digital-heritage-platform.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 步骤 3：在 Render 创建 Web 服务

#### 3.1 登录 Render

1. 访问 [https://dashboard.render.com](https://dashboard.render.com)
2. 使用 GitHub 账号登录并授权

#### 3.2 创建新服务

1. 点击右上角 **+ New** 按钮
2. 选择 **Web Service**

#### 3.3 配置 Web 服务

**基本信息：**

| 配置项 | 值 |
|--------|-----|
| Name | `digital-heritage-platform` |
| Region | `Oregon (US West)` 或离你最近的区域 |
| Branch | `main` |

**运行时配置：**

| 配置项 | 值 |
|--------|-----|
| Runtime | `Python` |
| Build Command | `apt-get update && apt-get install -y fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei && pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

**环境变量：**

| Key | Value | 说明 |
|-----|-------|------|
| `FLASK_ENV` | `production` | 生产环境 |
| `SECRET_KEY` | `your-secret-key-here` | Flask 密钥（自动生成或手动设置） |
| `DATABASE_URL` | （可选）见数据库配置 | PostgreSQL 连接字符串 |

**磁盘存储（可选但推荐）：**

| 配置项 | 值 |
|--------|-----|
| Name | `data` |
| Size | `1 GB` |
| Mount Path | `/opt/render/project/data` |

#### 3.4 部署

1. 点击 **Create Web Service**
2. 等待构建完成（首次部署约 3-5 分钟）
3. 部署成功后会显示访问 URL

---

## 方式二：通过 Docker 部署

### 步骤 1：构建 Docker 镜像

```bash
# 进入项目目录
cd "c:\Users\admin\Desktop\demo - codebuddy"

# 构建镜像
docker build -t digital-heritage-platform .
```

### 步骤 2：推送到 Docker Hub

```bash
# 登录 Docker Hub
docker login

# 标记镜像（替换 YOUR_USERNAME）
docker tag digital-heritage-platform YOUR_USERNAME/digital-heritage-platform:latest

# 推送到 Docker Hub
docker push YOUR_USERNAME/digital-heritage-platform:latest
```

### 步骤 3：在 Render 创建 Docker 服务

1. 在 Render Dashboard 点击 **+ New**
2. 选择 **Web Service**
3. 选择 **Dockerfile** 运行时
4. 输入 Docker Hub 镜像地址：`YOUR_USERNAME/digital-heritage-platform:latest`
5. 配置环境变量（同方式一）
6. 点击 **Create Web Service**

---

## 数据库配置

### 方案 A：使用 Supabase PostgreSQL（推荐）

#### 1. 创建 Supabase 项目

1. 访问 [https://supabase.com](https://supabase.com)
2. 使用 GitHub 账号登录
3. 点击 **New Project**
4. 填写项目信息：
   - Name: `digital-heritage-platform`
   - Database Password: 设置强密码
   - Region: 选择离 Render 最近的区域

#### 2. 获取数据库连接字符串

1. 进入项目 Dashboard
2. 点击左侧 **Settings** → **Database**
3. 找到 **Connection string**
4. 选择 **Python** 或 **URI**
5. 复制连接字符串，格式如下：

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

#### 3. 在 Render 配置环境变量

在 Render Web Service 的 **Environment** 标签页添加：

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres` |

#### 4. 初始化数据库表

部署成功后，访问应用会自动创建数据库表。或者手动运行：

```bash
# 在 Render Shell 中执行
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created!')"
```

### 方案 B：使用 SQLite（不推荐生产环境）

如果不想配置外部数据库，可以使用 SQLite（注意：Render 免费版重启后数据会丢失）

1. 在 Render 配置环境变量：

| Key | Value |
|-----|-------|
| `RENDER_DATA_DIR` | `/opt/render/project/data` |

2. 配置磁盘存储（1GB），挂载路径：`/opt/render/project/data`

---

## 环境变量配置

### 必需环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FLASK_ENV` | 运行环境 | `production` |
| `SECRET_KEY` | Flask 密钥 | `your-random-secret-key-12345` |

### 可选环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://user:pass@host:5432/db` |
| `RENDER_DATA_DIR` | 数据持久化目录 | `/opt/render/project/data` |

### 生成 SECRET_KEY

```bash
# Python 生成随机密钥
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 部署验证

### 1. 检查部署状态

在 Render Dashboard 查看：
- ✅ **Status**: `Live`
- ✅ **Health Check**: 通过
- ✅ **Build Logs**: 无错误

### 2. 访问应用

1. 点击 Render 提供的 URL（如：`https://digital-heritage-platform.onrender.com`）
2. 测试基本功能：
   - ✅ 首页加载
   - ✅ 用户注册/登录
   - ✅ 创建遗嘱
   - ✅ 生成 PDF（测试中文显示）

### 3. 测试 PDF 中文支持

1. 登录应用
2. 创建一个包含中文的遗嘱
3. 点击"生成 PDF"按钮
4. 下载并打开 PDF
5. 验证中文是否正确显示

### 4. 查看 Build Logs

如果出现问题，查看详细日志：

```bash
# 在 Render Dashboard
点击 Web Service → Logs → Build Logs
```

---

## 故障排除

### 问题 1：部署失败 - 字体安装错误

**错误信息：**
```
E: Unable to locate package fonts-noto-cjk
```

**解决方案：**

修改 `render.yaml` 的 buildCommand：

```yaml
buildCommand: apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei && pip install -r requirements.txt
```

### 问题 2：PDF 中文显示为方框

**原因：** 字体未正确加载

**解决方案：**

1. 在 Render Shell 中检查字体：

```bash
# 检查字体文件是否存在
ls -la /usr/share/fonts/truetype/wqy/

# 检查字体是否已安装
fc-list | grep -i "wqy\|noto"
```

2. 如果字体未安装，手动安装：

```bash
apt-get update
apt-get install -y fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei
fc-cache -fv
```

3. 重启服务：

```bash
# 在 Render Dashboard
点击 Web Service → Manual Deploy → Deploy latest commit
```

### 问题 3：数据库连接失败

**错误信息：**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**解决方案：**

1. 检查 `DATABASE_URL` 环境变量是否正确
2. 确认 Supabase 项目是否正在运行
3. 验证数据库密码是否正确
4. 检查 Supabase 的网络访问设置

### 问题 4：应用启动失败

**错误信息：**
```
ModuleNotFoundError: No module named 'reportlab'
```

**解决方案：**

1. 检查 `requirements.txt` 是否包含所有依赖
2. 重新部署：

```bash
# 在 Render Dashboard
点击 Web Service → Manual Deploy → Clear build cache & deploy
```

### 问题 5：磁盘空间不足

**错误信息：**
```
OSError: [Errno 28] No space left on device
```

**解决方案：**

1. 升级 Render 磁盘存储（付费）
2. 或定期清理临时文件：

```bash
# 在 Render Shell 中执行
rm -rf /tmp/*
rm -rf /opt/render/project/data/temp_pdfs/*
```

### 问题 6：PDF 生成超时

**错误信息：**
```
TimeoutError: PDF generation timeout
```

**解决方案：**

1. 优化 PDF 生成逻辑（减少字体加载时间）
2. 增加 Render 实例配置（升级到付费版本）
3. 使用异步任务队列（如 Celery + Redis）

---

## 常见问题 FAQ

### Q1: Render 免费版有什么限制？

**A:**
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ 每月 750 小时运行时间
- ✅ 自动休眠（15分钟无访问）
- ❌ 睡眠后唤醒需要 30-60 秒
- ❌ 数据在重启后会丢失（需要配置持久化）

### Q2: 如何避免应用自动休眠？

**A:**
- 升级到 Render Starter 计划（$7/月）
- 或使用外部服务定期 ping（如 UptimeRobot）

### Q3: Supabase 免费版有什么限制？

**A:**
- ✅ 500 MB 数据库存储
- ✅ 1 GB 文件存储
- ✅ 2GB 带宽/月
- ✅ 50,000 次请求/月
- ✅ 无限活跃用户

### Q4: 如何备份数据库？

**A:**

使用 Supabase 自动备份：
1. 进入 Supabase Dashboard
2. Settings → Database → Backups
3. 启用自动备份（每天备份）

或手动导出：

```bash
# 使用 pg_dump
pg_dump $DATABASE_URL > backup.sql
```

### Q5: 如何自定义域名？

**A:**

1. 在 Render Dashboard：
   - Web Service → Settings → Custom Domains
   - 添加你的域名（如 `app.yourdomain.com`）

2. 在域名 DNS 设置：
   - 添加 CNAME 记录指向 Render 提供的地址

### Q6: 如何监控应用性能？

**A:**

1. Render Dashboard 提供：
   - CPU 使用率
   - 内存使用率
   - 请求日志
   - 错误日志

2. 集成第三方监控（如 Sentry）：
   ```python
   # 在 app.py 中添加
   import sentry_sdk
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       traces_sample_rate=1.0,
   )
   ```

### Q7: 如何更新部署？

**A:**

```bash
# 本地修改代码后
git add .
git commit -m "Update: your changes"
git push

# Render 会自动检测并重新部署
```

或手动触发：
1. Render Dashboard → Web Service
2. 点击 **Manual Deploy** → **Deploy latest commit**

### Q8: 如何回滚到之前的版本？

**A:**

1. Render Dashboard → Web Service
2. 点击 **Events** 标签
3. 找到成功的部署记录
4. 点击 **Rollback** 按钮

### Q9: PDF 文件存储在哪里？

**A:**

- **开发环境**：`temp_pdfs/` 目录
- **生产环境**：`/opt/render/project/data/temp_pdfs/`

注意：Render 免费版重启后文件会丢失，建议：
- 使用对象存储（如 AWS S3、Cloudflare R2）
- 或升级到付费版本

### Q10: 如何查看详细的错误日志？

**A:**

1. Render Dashboard → Web Service → **Logs**
2. 选择日志类型：
   - **Build Logs**: 构建日志
   - **Deploy Logs**: 部署日志
   - **Runtime Logs**: 运行时日志
3. 使用搜索过滤特定错误：
   ```
   error, exception, failed
   ```

---

## 📞 技术支持

如果遇到问题：

1. 查看 [Render 文档](https://render.com/docs)
2. 查看 [Supabase 文档](https://supabase.com/docs)
3. 检查项目的 GitHub Issues

---

## 🎉 部署成功！

恭喜！你的数字遗产继承平台已成功部署到 Render。

**下一步：**
- 配置自定义域名
- 设置数据库定期备份
- 监控应用性能
- 根据用户反馈优化功能

**访问地址：** `https://your-app-name.onrender.com`

---

*最后更新：2026-02-14*
