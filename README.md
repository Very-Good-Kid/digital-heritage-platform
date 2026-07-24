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
- **AI智能对话**：RAG检索增强 + 流式SSE输出 + 视觉问答(图片理解) + 每日次数限制
- **AI知识库管理**：后台管理员上传文档构建知识库（PDF/TXT/MD/DOCX）
- 后台管理系统（用户管理、AI对话次数控制、知识库管理）

## 技术栈

- **后端**: Flask 3.0.3
- **数据库**: SQLite (本地) / Neon PostgreSQL (生产)
- **前端**: Bootstrap 5, Chart.js, marked.js
- **认证**: Flask-Login
- **安全**: Flask-WTF (CSRF保护)
- **加密**: PBKDF2HMAC 密钥派生 (600K) + Fernet 对称加密；ENCRYPTION_KEY 仅做启动期格式校验
- **AI**: 智谱AI(对话+视觉) + SiliconFlow(免费Embedding+备选对话) + RAG + Tavily搜索

### 加密技术说明

项目采用**基于主密码的密钥派生加密方案**（非"双层密钥"），符合《技术概要》要求：

1. **ENCRYPTION_KEY（启动期格式校验）**
   - 仅用于启动期校验密钥格式合法性；缺失或格式非法即 fail-fast 拒绝启动
   - **不参与实际加解密**，避免冗余密钥与误解

2. **PBKDF2HMAC 密钥派生（实际加密密钥来源）**
   - 算法: SHA256
   - 迭代次数: 600,000 次
   - 功能: 由 `ENCRYPTION_PASSWORD` 派生 Fernet 密钥，增强抗暴力破解能力

3. **Fernet 对称加密**
   - 算法: AES-128-CBC + HMAC-SHA256
   - 功能: 使用派生密钥对用户敏感信息进行端到端加密存储

4. **安全特性**
   - 平台仅存储加密后的密文，全程不接触用户明文信息
   - 每条记录使用独立随机盐，无全局固定盐
   - 符合《数据安全法》相关合规要求

### AI技术说明

项目采用**双后端**方案,最大化免费额度:

| 用途 | 主模型 | 备选模型 | 说明 |
|------|--------|----------|------|
| 文本对话 | 智谱AI glm-4-flash | SiliconFlow Qwen2.5-7B | 429排队时自动切换 |
| 视觉问答 | 智谱AI glm-4.6v-flash | glm-4.1v-thinking-flash | SiliconFlow无免费视觉模型 |
| 文本向量化 | SiliconFlow bge-large-zh-v1.5 | 智谱AI embedding-3 | 默认SiliconFlow(免费),中文专用 |

## 本地开发

### 环境要求

- Python 3.10+
- pip

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd V1.0-迭代中
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

5. 创建管理员
```bash
python scripts/create_admin.py
```

## 部署到 Render

### 方法一：通过 render.yaml（推荐）

1. 确保项目已推送到 GitHub
2. 登录 [Render](https://render.com)
3. 点击 "New +" → "Web Service"
4. 连接你的 GitHub 仓库
5. Render 会自动检测 `deploy/render.yaml` 文件
6. 点击 "Create Web Service"

### 方法二：手动配置

1. 登录 [Render](https://render.com)
2. 点击 "New +" → "Web Service"
3. 连接你的 GitHub 仓库
4. 配置以下内容：

**构建和部署**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120`

**环境变量**
- `FLASK_ENV`: `production`
- `SECRET_KEY`: 必需,由部署平台/密钥管理服务注入强随机值,缺失则拒绝启动
- `ENCRYPTION_KEY`: 必需,Fernet 加密密钥(服务端生成的安全随机串),缺失则拒绝启动
- `ENCRYPTION_PASSWORD`: 必需,PBKDF2 主密码(服务端生成的安全随机串),缺失则加解密失败
- `DATABASE_URL`: Neon PostgreSQL 连接字符串
- `ZHIPU_API_KEY`: 智谱AI API密钥（必需）
- `SILICONFLOW_API_KEY`: SiliconFlow API密钥（推荐，免费Embedding）

5. 点击 "Create Web Service"

### 首次部署后

部署完成后：
1. 在Render Shell中运行 `python scripts/create_admin.py` 创建管理员
2. 使用管理员账户登录后台管理系统
3. 在"AI功能→知识库管理"中上传法律文档构建知识库

## 数据库说明

### 本地与云端分离

| 环境 | 数据库 | 说明 |
|------|--------|------|
| 本地开发 | SQLite | `.env`中不设DATABASE_URL，使用instance/digital_heritage.db |
| 线上生产 | Neon PostgreSQL | 免费版5分钟无活动后休眠，首次请求冷启动2-5秒 |

### 数据同步

- **同步**: 知识库数据（管理员上传的法律文档）
- **不同步**: 用户数据、资产数据、遗嘱数据（涉及隐私）

```bash
# 知识库同步（本地SQLite → 云端Neon）
python scripts/sync_knowledge_to_neon.py           # 执行同步
python scripts/sync_knowledge_to_neon.py --dry-run # 仅预览
```

## 环境变量

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `SECRET_KEY` | 是 | Flask密钥,必须有值,缺失则拒绝启动 | 无默认值 |
| `ENCRYPTION_KEY` | 是 | Fernet 格式密钥(服务端生成的安全随机串),仅用于启动期格式校验,缺失或非法则拒绝启动 | 无默认值 |
| `ENCRYPTION_PASSWORD` | 是 | PBKDF2 主密码(服务端生成的安全随机串) | 无默认值 |
| `ZHIPU_API_KEY` | 是 | 智谱AI密钥（对话+视觉） | - |
| `SILICONFLOW_API_KEY` | 推荐 | SiliconFlow密钥（免费Embedding+备选对话） | - |
| `DATABASE_URL` | 线上 | Neon PostgreSQL连接串 | SQLite |
| `NEON_DATABASE_URL` | 否 | 仅同步脚本使用 | - |
| `EMBEDDING_PROVIDER` | 否 | Embedding提供者 | `siliconflow` |
| `TAVILY_API_KEY` | 否 | Tavily搜索密钥（不设则禁用搜索） | - |

## 项目结构

```
故里/
├── app.py                 # 主应用文件
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量
│
├── ai/                    # AI智能对话模块
│   ├── __init__.py
│   ├── llm.py             # 智谱AI(主)+SiliconFlow(备)
│   ├── embedding.py       # SiliconFlow(免费)+智谱AI(备)
│   ├── rag.py             # RAG核心
│   ├── search.py          # 网络搜索(Tavily)
│   ├── chunker.py         # 文本分块
│   └── document_parser.py # 文档解析
│
├── admin/                 # 后台管理模块
│   ├── __init__.py
│   ├── views.py
│   ├── stats.py
│   ├── crud.py
│   ├── auth.py
│   ├── decorators.py
│   ├── middleware.py
│   └── api_format.py
│
├── config/                # 配置模块
│   └── tenant.py
│
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── encryption.py      # 加密工具
│   ├── fonts.py           # 字体管理
│   └── pdf_generator.py   # PDF 生成
│
├── scripts/               # 运维脚本
│   ├── create_admin.py    # 创建管理员
│   ├── reset_admin_pwd.py # 重置管理员密码
│   ├── init_db.py         # 初始化数据库
│   └── sync_knowledge_to_neon.py # 知识库同步
│
├── docs/                  # 文档与业务资料
│   ├── AI_CONFIG_GUIDE.md # AI配置指南
│   ├── DEPLOYMENT_GUIDE.md # 部署指南
│   ├── CHANGELOG.md       # 更新日志
│   └── guides/            # 继承指引PDF
│       ├── 继承指引流程/   # 平台操作流程PDF(10个)
│       └── 继承指引模板/   # 法律模板PDF(4个)
│
├── deploy/                # 部署配置
│   ├── render.yaml        # Render部署配置
│   ├── render-build.sh    # Render构建脚本
│   ├── render_init.py     # Render初始化
│   ├── Dockerfile         # Docker构建
│   ├── Procfile           # 进程配置
│   ├── runtime.txt        # Python版本
│   ├── install_fonts_runtime.py # 运行时字体安装
│   ├── install_fonts.sh   # Shell字体安装
│   └── 启动网站.bat       # 本地启动
│
├── templates/             # 前端模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── about.html         # 关于页
│   ├── auth/              # 认证(登录/注册)
│   ├── assets/            # 资产管理
│   ├── dashboard/         # 用户仪表盘
│   ├── wills/             # 遗嘱管理
│   ├── policies/          # 平台政策
│   ├── inheritance/       # 继承导航
│   ├── inheritance-guide/ # 继承指引
│   ├── chat/              # AI智能对话
│   ├── faq/               # FAQ
│   ├── care/              # 关怀
│   ├── errors/            # 错误页(404/500)
│   └── admin/             # 后台管理
│       ├── base.html      # 后台基模板
│       ├── dashboard.html # 仪表盘
│       ├── users.html     # 用户管理
│       ├── assets.html    # 资产管理
│       ├── wills.html     # 遗嘱管理
│       ├── policies.html  # 政策管理
│       ├── stories.html   # 故事墙管理
│       ├── faqs.html      # FAQ管理
│       ├── knowledge.html # 知识库管理
│       ├── settings.html  # 系统设置
│       └── sync.html      # 数据同步
│
├── static/                # 静态文件
│   ├── fonts/             # 字体文件
│   ├── templates/         # PDF 模板
│   └── uploads/           # 用户上传
│
└── instance/              # 实例数据
    ├── digital_heritage.db # SQLite 数据库
    └── temp_pdfs/         # 临时 PDF 文件
```

## 文档

- [AI配置指南](docs/AI_CONFIG_GUIDE.md) - AI功能配置说明（双后端方案）
- [部署指南](docs/DEPLOYMENT_GUIDE.md) - Render云服务部署指南
- [更新日志](docs/CHANGELOG.md) - 版本更新记录

## 许可证

MIT License
