# 数字遗产继承平台

一个帮助用户规划和管理数字遗产的Flask Web应用。

## 功能特性

- 用户认证系统（注册、登录、登出）
- 数字资产管理（社交、金融、记忆、虚拟财产）
- 数字遗嘱创建和管理
- 平台政策矩阵展示
- 数字资产继承导航
- 故事墙
- 常见问题解答（FAQ）
- 后台管理系统

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLite
- **前端**: Bootstrap 5, Chart.js
- **认证**: Flask-Login
- **安全**: Flask-WTF (CSRF保护)

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

## 部署到Render

### 方法一：通过 render.yaml（推荐）

1. 确保项目已推送到GitHub
2. 登录 [Render](https://render.com)
3. 点击 "New +" → "Web Service"
4. 连接你的GitHub仓库
5. Render会自动检测 `render.yaml` 文件
6. 点击 "Create Web Service"

### 方法二：手动配置

1. 登录 [Render](https://render.com)
2. 点击 "New +" → "Web Service"
3. 连接你的GitHub仓库
4. 配置以下内容：

**构建和部署**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**环境变量**
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (自动生成或自定义)
- `RENDER_DATA_DIR`: `/opt/render/project/data`

**持久化磁盘**
- **Disk Name**: `data`
- **Size**: `1 GB`
- **Mount Path**: `/opt/render/project/data`

5. 点击 "Create Web Service"

### 数据持久化

应用使用Render的持久化磁盘来存储：
- SQLite数据库文件
- 上传的文件
- 生成的PDF文件

### 首次部署后

部署完成后，访问应用并：
1. 注册一个管理员账户
2. 在数据库中将该用户的 `is_admin` 字段设置为 `True`
3. 使用管理员账户登录后台管理系统

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | 运行环境 | `production` |
| `SECRET_KEY` | Flask密钥 | 自动生成 |
| `RENDER_DATA_DIR` | 数据目录 | `/opt/render/project/data` |

## 项目结构

```
demo - codebuddy/
├── admin/                 # 后台管理模块
│   ├── __init__.py
│   ├── views.py
│   └── templates/        # 后台管理模板
├── models.py             # 数据库模型
├── utils/                # 工具模块
│   ├── encryption.py     # 加密工具
│   └── pdf_generator.py  # PDF生成
├── templates/            # 前端模板
│   ├── admin/
│   ├── auth/
│   ├── assets/
│   ├── dashboard/
│   ├── faq/
│   ├── inheritance-guide/
│   ├── policies/
│   ├── stories/
│   └── wills/
├── static/               # 静态文件
├── app.py               # 主应用文件
├── config.py            # 配置文件
├── requirements.txt     # Python依赖
├── render.yaml          # Render配置
├── Procfile             # 进程文件
└── README.md            # 项目说明
```

## 许可证

MIT License
