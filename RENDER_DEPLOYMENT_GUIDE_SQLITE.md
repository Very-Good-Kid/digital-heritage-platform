# 数字遗产继承平台 - Render.com 完全免费部署指南（SQLite版本）

## 概述

本指南将帮助您将数字遗产继承平台部署到 Render.com 免费云服务器上，使用 SQLite 数据库实现**完全免费**的部署，无需任何付费服务。

## 完全免费方案的优势

✅ **永久免费** - 无需支付任何费用
✅ **无时间限制** - 不像 PostgreSQL 数据库只有90天试用
✅ **数据持久化** - 使用 Render 的持久化磁盘存储数据库
✅ **简单部署** - 无需创建和管理数据库
✅ **适合个人项目** - 适合轻量级应用和演示项目

## 免费额度说明

### Web Service（永久免费）
- **512 MB RAM**
- **0.1 CPU**
- **每月 750 小时运行时间**
- **1 GB 持久化磁盘**（用于存储数据库和上传文件）
- **自动休眠**：15 分钟无访问后休眠
- **冷启动时间**：约 30-60 秒

### 注意事项
1. 免费计划会在 15 分钟无访问后自动休眠（这是正常的）
2. 下次访问时需要等待 30-60 秒启动
3. SQLite 数据库存储在持久化磁盘中，数据不会丢失
4. 适合个人项目、演示项目和小型应用

## 准备工作

### 1. 必需账户
- [ ] GitHub 账户（免费）
- [ ] Render.com 账户（免费）
- [ ] 域名（可选，用于自定义域名）

### 2. 本地准备
- [ ] 确保项目代码已经准备完成
- [ ] 已创建所有必要的配置文件（已完成）
- [ ] 已安装 Git

## 部署步骤

### 第一步：创建 GitHub 仓库

1. 登录 GitHub 网站（https://github.com）
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `digital-heritage-platform`（或其他名称）
   - Description: `数字遗产继承平台`
   - 选择 Public 或 Private（推荐 Public）
4. 点击 "Create repository" 创建仓库

### 第二步：推送代码到 GitHub

在本地项目目录打开命令行（PowerShell 或 CMD），执行以下命令：

```bash
# 初始化 Git 仓库（如果还没有初始化）
git init

# 添加所有文件到暂存区
git add .

# 提交更改
git commit -m "Initial commit - 数字遗产继承平台（SQLite版本）"

# 添加远程仓库（替换 YOUR_USERNAME 为您的 GitHub 用户名）
git remote add origin https://github.com/Very-Good-Kid/digital-heritage-platform.git

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

### 第三步：在 Render.com 创建账户

1. 访问 Render.com（https://render.com）
2. 点击 "Sign Up" 注册账户
3. 选择使用 GitHub 账户登录（推荐）
4. 授权 Render.com 访问您的 GitHub 仓库

### 第四步：创建 Web 服务（使用 SQLite）

1. 登录 Render.com 后，点击 "New +" 按钮
2. 选择 "Web Service"
3. 连接 GitHub 仓库：
   - 在 "Build and deploy from a Git repository" 部分
   - 点击 "Connect" 按钮连接您的 GitHub 账户
   - 选择 `digital-heritage-platform` 仓库
   - 选择 `main` 分支
4. **Render 会自动检测 `render.yaml` 配置文件，自动填充以下配置：**
   - Name: `digital-heritage-platform`
   - Region: 选择离您最近的区域（如 Singapore 或 Oregon）
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: Free（自动选择）
   - Disk: 1 GB（自动配置）

5. **环境变量会自动配置**（无需手动设置）：
   - `PYTHON_VERSION`: `3.9.0`
   - `SECRET_KEY`: 自动生成
   - `DATABASE_URL`: `sqlite:////opt/render/project/data/digital_heritage.db`
   - `FLASK_ENV`: `production`

6. 点击 "Create Web Service" 创建服务

### 第五步：等待部署完成

1. 部署过程通常需要 2-5 分钟
2. 您可以在 "Logs" 标签查看部署日志
3. 部署完成后会看到 "Live" 状态
4. 点击服务 URL 访问您的网站

### 第六步：初始化数据库

部署完成后，需要手动初始化数据库：

1. 在 Render.com 控制台，点击您的 Web 服务
2. 点击 "Shell" 标签（进入命令行）
3. 执行以下命令：

```bash
python init_db.py
```

4. 等待数据库初始化完成，看到 "✓ 数据库初始化完成！" 提示
5. 退出 Shell，访问您的网站

### 第七步：验证部署

1. 访问您的网站 URL（格式：https://digital-heritage-platform.onrender.com）
2. 测试网站功能：
   - 访问首页
   - 注册账户
   - 登录系统
   - 添加数字资产
   - 创建数字遗嘱
   - 生成 PDF
   - 测试其他功能

## 项目配置文件说明

### 1. render.yaml（已更新）
```yaml
services:
  - type: web
    name: digital-heritage-platform
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        value: sqlite:////opt/render/project/data/digital_heritage.db
      - key: FLASK_ENV
        value: production
    disk:
      name: data
      mountPath: /opt/render/project/data
      sizeGB: 1
```

**关键配置说明：**
- `DATABASE_URL`: 使用 SQLite 数据库，存储在持久化磁盘中
- `disk`: 配置 1GB 持久化磁盘，确保数据不会丢失
- `mountPath`: 数据库存储路径

### 2. Procfile
```
web: gunicorn app:app
```
告诉 Render 使用 Gunicorn 作为 WSGI 服务器。

### 3. requirements.txt（已更新）
移除了 PostgreSQL 依赖，只包含必需的包：
- `gunicorn==21.2.0` - WSGI 服务器
- 其他 Flask 相关依赖

### 4. config.py（已更新）
优化了生产环境配置，支持 SQLite 数据库和持久化磁盘。

### 5. init_db.py（新增）
数据库初始化脚本，用于创建数据库表和初始化示例数据。

### 6. .gitignore
确保敏感文件和临时文件不会被提交到 GitHub。

## 自定义域名（可选）

如果您有自己的域名，可以按照以下步骤配置：

### 1. 在 Render.com 添加自定义域名

1. 在 Web 服务页面，点击 "Settings"
2. 在 "Custom Domains" 部分，点击 "Add Custom Domain"
3. 输入您的域名（如 `www.yourdomain.com`）
4. 点击 "Add Domain"

### 2. 配置 DNS 记录

1. 记录 Render.com 提供的 DNS 信息
2. 登录您的域名注册商（如阿里云、腾讯云、GoDaddy 等）
3. 添加以下 DNS 记录：

   **CNAME 记录（推荐）：**
   - Type: CNAME
   - Name: www
   - Value: `your-service-name.onrender.com`

4. 保存 DNS 设置

### 3. 启用 HTTPS

1. 在 Render.com 的自定义域名页面
2. 点击 "Enable HTTPS" 按钮
3. 等待 SSL 证书自动生成（通常需要几分钟）

## 数据持久化说明

### SQLite 数据库存储位置
- **路径**: `/opt/render/project/data/digital_heritage.db`
- **存储**: 使用 Render 的 1GB 持久化磁盘
- **持久性**: 数据不会因为应用重启而丢失

### 上传文件存储位置
- **路径**: `/opt/render/project/uploads/`
- **存储**: 同样使用持久化磁盘
- **持久性**: 上传的文件不会丢失

### 数据备份建议
虽然数据存储在持久化磁盘中，但建议定期备份数据库：

1. 在 Render Shell 中执行：
```bash
cp /opt/render/project/data/digital_heritage.db /opt/render/project/data/backup_$(date +%Y%m%d).db
```

2. 或使用 Render 的自动备份功能（需要升级到付费计划）

## 监控和维护

### 查看日志
1. 在 Render.com 控制台
2. 点击您的 Web 服务
3. 点击 "Logs" 标签查看实时日志

### 更新代码
1. 在本地修改代码
2. 提交到 GitHub：
   ```bash
   git add .
   git commit -m "描述您的更改"
   git push
   ```
3. Render 会自动检测到更改并重新部署

### 重新初始化数据库
如果需要重新初始化数据库：
1. 在 Render Shell 中执行：
   ```bash
   rm /opt/render/project/data/digital_heritage.db
   python init_db.py
   ```

## 常见问题

### 1. 部署失败
- 检查构建日志，查看具体错误信息
- 确保所有依赖都在 requirements.txt 中
- 检查 Python 版本兼容性

### 2. 数据库连接错误
- 确认 DATABASE_URL 环境变量已正确设置
- 检查 init_db.py 是否已执行
- 验证数据目录是否存在

### 3. 静态文件无法加载
- 确保 static 目录结构正确
- 检查 CSS/JS 文件路径
- 清除浏览器缓存

### 4. 应用休眠（这是正常的）
- 免费计划的正常行为
- 下次访问需要等待 30-60 秒启动
- 如果不希望休眠，可以使用保活服务（如 UptimeRobot）

### 5. 数据丢失
- 确保数据库存储在持久化磁盘中（/opt/render/project/data/）
- 定期备份数据库
- 检查磁盘使用情况（1GB 限制）

### 6. 如何避免休眠
使用免费保活服务：
1. 注册 UptimeRobot（https://uptimerobot.com）
2. 添加监控：每 5 分钟访问一次您的网站
3. 这样可以保持应用始终运行

## 性能优化建议

### 1. 数据库优化
- 为常用查询字段添加索引
- 定期清理过期数据
- 优化 SQL 查询

### 2. 静态资源优化
- 压缩 CSS 和 JS 文件
- 优化图片大小
- 使用 CDN 加速（可选）

### 3. 应用优化
- 减少数据库查询
- 使用缓存机制
- 优化代码逻辑

## 安全建议

1. **环境变量**：不要在代码中硬编码敏感信息
2. **HTTPS**：始终使用 HTTPS 加密传输
3. **定期更新**：及时更新依赖包版本
4. **备份**：定期备份数据库和重要文件
5. **监控**：定期检查日志，发现异常及时处理

## 与 PostgreSQL 版本对比

| 特性 | SQLite 版本 | PostgreSQL 版本 |
|------|------------|----------------|
| **费用** | 完全免费 | 90天免费，之后$7/月起 |
| **部署复杂度** | 简单 | 中等 |
| **数据持久性** | 好（持久化磁盘） | 优秀 |
| **性能** | 适合小规模应用 | 适合大规模应用 |
| **并发支持** | 有限 | 良好 |
| **适合场景** | 个人项目、演示、小型应用 | 生产环境、大型应用 |

## 下一步

部署完成后，您可以：

1. **测试功能**：全面测试网站所有功能
2. **配置域名**：设置自定义域名（如果需要）
3. **设置保活**：使用 UptimeRobot 避免应用休眠
4. **监控性能**：使用 Render 的监控工具
5. **收集反馈**：邀请用户测试并收集反馈
6. **持续改进**：根据反馈不断优化功能

## 技术支持

如遇到问题，可以：

1. 查看 Render 文档：https://render.com/docs
2. 查看 Render 状态页面：https://status.render.com
3. 联系 Render 支持：support@render.com
4. 查看项目文档：PROJECT_SUMMARY.md、README.md

## 总结

恭喜！按照本指南，您已成功将数字遗产继承平台部署到 Render.com 免费云服务器上，使用 SQLite 数据库实现**完全免费**的部署。

**您的网站地址**：`https://digital-heritage-platform.onrender.com`（或您的自定义域名）

**完全免费** - 无需支付任何费用，永久使用！

---

**部署完成日期**：2026年
**部署平台**：Render.com
**数据库**：SQLite
**版本**：V1.0
**费用**：完全免费
