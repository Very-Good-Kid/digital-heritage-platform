# 更新日志 (Changelog)

本文档记录项目的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [Unreleased]

### 新增
- 项目文件整合和清理

---

## [1.0.0] - 2026-02-25

### 新增
- 用户认证系统（注册、登录、登出）
- 数字资产管理（社交、金融、记忆、虚拟财产）
- 数字资产处置意愿声明书创建和管理
- 平台政策矩阵展示
- 数字资产继承导航
- 故事墙功能
- 常见问题解答（FAQ）
- 后台管理系统
- Render 云服务部署支持
- Neon PostgreSQL 数据库支持

### 修复

#### 2026-02-25 安全漏洞修复
- **问题**: GitGuardian 检测到 PostgreSQL 数据库密码在 Render 部署日志中泄露
- **修复**: 
  - 移除 `config.py` 中打印数据库连接字符串的代码
  - 更新 `.gitignore` 文件，确保环境变量文件不被提交
- **建议**: 立即轮换 Neon 数据库密码

#### 2026-02-25 数据库连接修复
- **问题**: 部署到 Render 后出现 SSL 连接错误
  ```
  psycopg2.OperationalError: SSL connection has been closed unexpectedly
  ```
- **修复**:
  - 添加 SSL 连接参数 `sslmode=require`
  - 添加连接池回收参数 `pool_recycle=3600`
  - 添加数据库连接健康检查中间件

#### 2026-02-25 SQLite URI 格式修复
- **问题**: SQLite 数据库无法打开
  ```
  sqlalchemy.exc.OperationalError: unable to open database file
  ```
- **修复**:
  - 修正 SQLite URI 格式，绝对路径使用 4 个斜杠 `sqlite:////`
  - 添加 Windows 控制台 UTF-8 编码支持
  - 应用启动时自动创建数据目录

#### 2026-02-25 CSRF 错误修复
- **问题**: Render 生产环境登录失败
  ```
  AttributeError: 'CustomCSRFProtect' object has no attribute 'app'
  ```
- **修复**: 添加安全检查，确保 `self.app` 属性存在后再访问

#### 2026-02-25 管理员后台修复
- **问题**: Render 上管理员后台显示 Internal Server Error
- **修复**:
  - 删除 `admin/stats.py` 中的重复代码
  - 添加错误处理，避免数据库查询失败导致页面崩溃
  - 优化 PostgreSQL 兼容性

### 变更

#### 数据库同步策略
- **策略**: 仅同步 FAQ 数据，不同步用户敏感数据
- **原因**:
  - 用户数据涉及隐私，不应在生产和开发环境之间同步
  - 资产数据是用户的个人数据
  - FAQ 是公开内容，可以安全同步
- **工具**: 使用 `sync_faq_to_neon.py` 脚本同步 FAQ 数据

---

## 部署指南

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 访问地址
http://localhost:5000
```

### Render 部署
1. 推送代码到 GitHub
2. Render 自动部署
3. 配置环境变量：
   - `DATABASE_URL`: Neon PostgreSQL 连接字符串
   - `SECRET_KEY`: 随机生成的密钥
   - `FLASK_ENV`: production

### FAQ 数据同步
```bash
# 从本地导出 FAQ 数据
python sync_faq_to_neon.py
```

---

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLite (本地) / PostgreSQL (生产)
- **前端**: Bootstrap 5, Chart.js
- **认证**: Flask-Login
- **安全**: Flask-WTF (CSRF保护)

---

## 许可证

MIT License
