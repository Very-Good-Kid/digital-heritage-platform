# 数字遗产继承平台 - Render.com 部署指南

## 概述

本指南将帮助您将数字遗产继承平台部署到 Render.com 免费云服务器上，让其他人可以通过域名直接访问。

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

在本地项目目录打开命令行，执行以下命令：

```bash
# 初始化 Git 仓库（如果还没有初始化）
git init

# 添加所有文件到暂存区
git add .

# 提交更改
git commit -m "Initial commit - 数字遗产继承平台"

# 添加远程仓库（替换 YOUR_USERNAME 为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/digital-heritage-platform.git

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

### 第三步：在 Render.com 创建账户

1. 访问 Render.com（https://render.com）
2. 点击 "Sign Up" 注册账户
3. 选择使用 GitHub 账户登录（推荐）
4. 授权 Render.com 访问您的 GitHub 仓库

### 第四步：创建 Web 服务

1. 登录 Render.com 后，点击 "New +" 按钮
2. 选择 "Web Service"
3. 连接 GitHub 仓库：
   - 在 "Build and deploy from a Git repository" 部分
   - 点击 "Connect" 按钮连接您的 GitHub 账户
   - 选择 `digital-heritage-platform` 仓库
   - 选择 `main` 分支
4. 配置服务：
   - Name: `digital-heritage-platform`
   - Region: 选择离您最近的区域（如 Singapore 或 Oregon）
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

5. 配置环境变量（Advanced 部分）：
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: 生成一个随机密钥（可以使用 https://randomkeygen.com/）

6. 点击 "Create Web Service" 创建服务

### 第五步：创建数据库

1. 在 Render.com 控制台中，点击 "New +"
2. 选择 "PostgreSQL"
3. 配置数据库：
   - Name: `digital-heritage-db`
   - Database Name: `digital_heritage`
   - User: `digital_heritage_user`
   - Region: 与 Web 服务相同
   - PostgreSQL Version: 选择最新版本
4. 点击 "Create Database" 创建数据库

### 第六步：连接数据库到 Web 服务

1. 创建数据库后，返回到您的 Web 服务页面
2. 点击 "Settings" 标签
3. 在 "Environment" 部分点击 "Add Environment Variable"
4. 添加以下环境变量：
   - Name: `DATABASE_URL`
   - Value: 从数据库页面复制 "Internal Database URL"
5. 点击 "Save Changes"
6. 点击 "Manual Deploy" → "Clear build cache & deploy"

### 第七步：验证部署

1. 等待部署完成（通常需要 2-5 分钟）
2. 在 Web 服务页面会看到 "Live" 状态
3. 点击服务 URL 访问您的网站（格式：https://digital-heritage-platform.onrender.com）
4. 测试网站功能：
   - 访问首页
   - 注册账户
   - 测试各项功能

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

   **A 记录（如果 Render 提供 IP）：**
   - Type: A
   - Name: @ 或 www
   - Value: Render 提供的 IP 地址

   **CNAME 记录（推荐）：**
   - Type: CNAME
   - Name: www
   - Value: `your-service-name.onrender.com`

4. 保存 DNS 设置

### 3. 启用 HTTPS

1. 在 Render.com 的自定义域名页面
2. 点击 "Enable HTTPS" 按钮
3. 等待 SSL 证书自动生成（通常需要几分钟）

## 项目配置文件说明

### 1. render.yaml
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
        fromDatabase:
          name: digital-heritage-db
          property: connectionString
    disk:
      name: data
      mountPath: /opt/render/project/uploads
      sizeGB: 1

databases:
  - name: digital-heritage-db
    databaseName: digital_heritage
    user: digital_heritage_user
```

### 2. Procfile
```
web: gunicorn app:app
```
告诉 Render 使用 Gunicorn 作为 WSGI 服务器。

### 3. requirements.txt
已添加生产环境必需的依赖：
- `gunicorn==21.2.0` - WSGI 服务器
- `psycopg2-binary==2.9.9` - PostgreSQL 数据库驱动

### 4. .gitignore
确保敏感文件和临时文件不会被提交到 GitHub。

## 免费额度说明

Render.com 免费计划包括：

### Web Service
- **512 MB RAM**
- **0.1 CPU**
- **每月 750 小时运行时间**
- **自动休眠**：15 分钟无访问后休眠
- **冷启动时间**：约 30-60 秒

### PostgreSQL 数据库
- **90 天免费试用**
- 试用期后需要升级到付费计划（$7/月起）

### 注意事项
1. 免费计划会在 15 分钟无访问后自动休眠
2. 下次访问时需要等待 30-60 秒启动
3. 数据库试用期结束后需要升级付费计划
4. 免费计划适合个人项目和轻量级应用

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

### 数据库备份
Render.com 自动每天备份 PostgreSQL 数据库，保留 7 天。

## 常见问题

### 1. 部署失败
- 检查构建日志，查看具体错误信息
- 确保所有依赖都在 requirements.txt 中
- 检查 Python 版本兼容性

### 2. 数据库连接错误
- 确认 DATABASE_URL 环境变量已正确设置
- 检查数据库是否正在运行
- 验证数据库凭据是否正确

### 3. 静态文件无法加载
- 确保 static 目录结构正确
- 检查 CSS/JS 文件路径
- 清除浏览器缓存

### 4. 应用休眠
- 这是免费计划的正常行为
- 升级到付费计划可避免休眠
- 或者使用保活服务（如 UptimeRobot）

### 5. 自定义域名无法访问
- 检查 DNS 记录是否正确配置
- 确认 DNS 已生效（可能需要 24-48 小时）
- 验证 HTTPS 证书是否已生成

## 安全建议

1. **环境变量**：不要在代码中硬编码敏感信息
2. **HTTPS**：始终使用 HTTPS 加密传输
3. **定期更新**：及时更新依赖包版本
4. **备份**：定期备份数据库和重要文件
5. **监控**：定期检查日志，发现异常及时处理

## 性能优化

1. **数据库索引**：为常用查询字段添加索引
2. **缓存**：使用 Redis 缓存频繁访问的数据
3. **静态文件**：使用 CDN 加速静态资源加载
4. **图片优化**：压缩和优化图片大小
5. **代码优化**：减少数据库查询，优化算法

## 下一步

部署完成后，您可以：

1. **测试功能**：全面测试网站所有功能
2. **配置域名**：设置自定义域名（如果需要）
3. **监控性能**：使用 Render 的监控工具
4. **收集反馈**：邀请用户测试并收集反馈
5. **持续改进**：根据反馈不断优化功能

## 技术支持

如遇到问题，可以：

1. 查看 Render 文档：https://render.com/docs
2. 查看 Render 状态页面：https://status.render.com
3. 联系 Render 支持：support@render.com
4. 查看项目文档：PROJECT_SUMMARY.md、README.md

## 总结

恭喜！按照本指南，您已成功将数字遗产继承平台部署到 Render.com 免费云服务器上。现在任何人都可以通过互联网访问您的网站，无需下载任何文件。

**您的网站地址**：`https://digital-heritage-platform.onrender.com`（或您的自定义域名）

---

**部署完成日期**：2026年
**部署平台**：Render.com
**版本**：V1.0
