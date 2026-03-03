# 一站式数字资产规划与继承服务平台

一个帮助用户规划和管理数字资产的 Flask Web 应用。

## 项目定位

**公益性数字资产规划与继承服务平台**

本项目致力于为普通大众提供低门槛的数字资产规划与继承服务。平台核心功能面向用户**免费开放**,降低数字资产规划门槛,让更多人能够享受到专业的数字资产保护服务。

### 核心价值

- **技术普惠**: 将专业级数字资产保护技术简化为零门槛可操作的功能
- **全链闭环**: 提供从资产盘点、意愿留存到继承指引的一站式闭环服务
- **合规可靠**: 严格参照国家法律法规与主流平台官方规则设计全流程功能
- **公益普惠**: 以极低成本轻量化架构实现普惠服务,核心功能面向大众长期免费开放

## 功能特性

- 用户认证系统（注册、登录、登出）
- 数字资产管理（社交、金融、记忆、虚拟财产）
- 数字资产处置意愿声明书创建和管理
- 平台政策矩阵展示
- 数字资产继承导航
- 故事墙
- 常见问题解答（FAQ）
- 后台管理系统

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLite (本地) / PostgreSQL (生产)
- **前端**: Bootstrap 5, Chart.js
- **认证**: Flask-Login
- **安全**: Flask-WTF (CSRF保护)
- **加密**: Fernet 对称加密 + PBKDF2HMAC 密钥派生 (双层加密方案)

### 加密技术说明

项目采用**双层加密方案**,符合《技术概要》要求:

1. **PBKDF2HMAC密钥派生**
   - 算法: SHA256
   - 迭代次数: 100,000次
   - 功能: 从密码派生加密密钥,增强抗暴力破解能力

2. **Fernet对称加密**
   - 算法: AES-128-CBC + HMAC-SHA256
   - 功能: 对用户敏感信息进行端到端加密存储

3. **安全特性**
   - 平台仅存储加密后的密文,全程不接触用户明文信息
   - 支持向后兼容,可灵活切换加密方式
   - 符合《数据安全法》相关合规要求

## 本地开发

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd demo - codebuddy
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 部署到 Render

### 方法一：通过 render.yaml（推荐）

1. 确保项目已推送到 GitHub
2. 登录 [Render](https://render.com)
3. 点击 "New +" → "Web Service"
4. 连接你的 GitHub 仓库
5. Render 会自动检测 `render.yaml` 文件
6. 点击 "Create Web Service"

### 方法二：手动配置

1. 登录 [Render](https://render.com)
2. 点击 "New +" → "Web Service"
3. 连接你的 GitHub 仓库
4. 配置以下内容：

**构建和部署**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**环境变量**
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (自动生成或自定义)
- `DATABASE_URL`: Neon PostgreSQL 连接字符串（可选）
- `RENDER_DATA_DIR`: `/opt/render/project/data`

**持久化磁盘**
- **Disk Name**: `data`
- **Size**: `1 GB`
- **Mount Path**: `/opt/render/project/data`

5. 点击 "Create Web Service"

### 数据持久化

应用使用 Render 的持久化磁盘来存储：
- SQLite 数据库文件（如未使用 PostgreSQL）
- 上传的文件
- 生成的 PDF 文件

### 首次部署后

部署完成后，访问应用并：
1. 注册一个管理员账户
2. 在数据库中将该用户的 `is_admin` 字段设置为 `True`
3. 使用管理员账户登录后台管理系统

## 数据库同步

### 同步策略

- **同步**: FAQ 数据（公开内容）
- **不同步**: 用户数据、资产数据、遗嘱数据（涉及隐私）

### 同步 FAQ 数据

```bash
# 从本地导出 FAQ 数据到 Neon PostgreSQL
python sync_faq_to_neon.py
```

详细说明请参考 [RENDER_SYNC_GUIDE.md](RENDER_SYNC_GUIDE.md)。

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | 运行环境 | `production` |
| `SECRET_KEY` | Flask 密钥 | 自动生成 |
| `DATABASE_URL` | PostgreSQL 连接字符串 | - |
| `RENDER_DATA_DIR` | 数据目录 | `/opt/render/project/data` |

## 项目结构

```
demo - codebuddy/
├── admin/                 # 后台管理模块
│   ├── __init__.py
│   ├── views.py
│   ├── stats.py
│   ├── crud.py
│   └── decorators.py
├── config/                # 配置模块
├── utils/                 # 工具模块
│   ├── encryption.py      # 加密工具
│   └── pdf_generator.py   # PDF 生成
├── templates/             # 前端模板
│   ├── admin/            # 后台管理模板
│   ├── auth/             # 认证模板
│   ├── assets/           # 资产管理模板
│   ├── dashboard/        # 仪表盘模板
│   ├── faq/              # FAQ 模板
│   ├── inheritance-guide/# 继承导航模板
│   ├── policies/         # 平台政策模板
│   ├── stories/          # 故事墙模板
│   └── wills/            # 遗嘱模板
├── static/                # 静态文件
│   ├── fonts/            # 字体文件
│   └── templates/        # PDF 模板
├── instance/              # 实例数据
│   ├── digital_heritage.db  # SQLite 数据库
│   └── temp_pdfs/        # 临时 PDF 文件
├── app.py                 # 主应用文件
├── models.py              # 数据库模型
├── config.py              # 配置文件
├── requirements.txt       # Python 依赖
├── render.yaml            # Render 配置
├── Procfile               # 进程文件
├── CHANGELOG.md           # 更新日志
└── README.md              # 项目说明
```

## 文档

- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [RENDER_SYNC_GUIDE.md](RENDER_SYNC_GUIDE.md) - 数据同步指南
- [NEON_SETUP_GUIDE.md](NEON_SETUP_GUIDE.md) - Neon 数据库配置指南
- [DOCS_INDEX.md](DOCS_INDEX.md) - 文档索引

## 许可证

MIT License
