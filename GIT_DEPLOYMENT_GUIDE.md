# 🚀 通过 Git 仓库部署到 Render（推荐）

## ✅ 已完成的工作

我已经帮你完成了以下步骤：

### 1. ✅ 初始化 Git 仓库
```bash
Git 仓库已初始化在: c:\Users\admin\Desktop\demo - codebuddy\.git
```

### 2. ✅ 配置 .gitignore
已创建完整的 `.gitignore` 文件，排除了：
- Python 缓存文件
- 虚拟环境
- 本地数据库文件
- 临时文件和日志
- IDE 配置文件

### 3. ✅ 提交代码到本地仓库
```bash
提交信息: "Initial commit: Digital Heritage Platform with Chinese font support"
提交哈希: 08b90eb
```

---

## 📋 接下来的步骤

### 步骤 1：创建 GitHub 仓库

#### 方法 A：通过网页创建（推荐）

1. **访问 GitHub**
   - 打开浏览器，访问：[https://github.com/new](https://github.com/new)
   - 登录你的 GitHub 账号（如果没有账号，先注册）

2. **创建新仓库**
   - **Repository name**: `digital-heritage-platform`
   - **Description**: `数字遗产继承平台 - 支持中文 PDF 生成`
   - **Visibility**: 选择 `Public`（公开）或 `Private`（私有）
   - ✅ **不要勾选** "Add a README file"
   - ✅ **不要勾选** "Add .gitignore"
   - ✅ **不要勾选** "Choose a license"

3. **点击 "Create repository"**

#### 方法 B：通过 GitHub CLI 创建

```bash
# 安装 GitHub CLI（如果还没安装）
# Windows: 下载安装 https://cli.github.com/

# 登录 GitHub
gh auth login

# 创建仓库
gh repo create digital-heritage-platform --public --description "数字遗产继承平台"

# 推送代码
git -C "c:\Users\admin\Desktop\demo - codebuddy" push -u origin main
```

---

### 步骤 2：连接 GitHub 仓库

#### 找到你的 GitHub 用户名

1. 访问 [https://github.com/settings/profile](https://github.com/settings/profile)
2. 查看 **Username** 字段（例如：`your-username`）

#### 添加远程仓库并推送

**替换 `YOUR_USERNAME` 为你的 GitHub 用户名**

```bash
# 进入项目目录
cd "c:\Users\admin\Desktop\demo - codebuddy"

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/digital-heritage-platform.git

# 验证远程仓库
git remote -v

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

**如果需要身份验证：**

- **方式 1：使用 Personal Access Token (推荐)**
  1. 访问 [https://github.com/settings/tokens](https://github.com/settings/tokens)
  2. 点击 "Generate new token" → "Generate new token (classic)"
  3. 勾选 `repo` 权限
  4. 生成 token 并复制
  5. 推送时输入：
     - Username: `YOUR_USERNAME`
     - Password: `your-github-token`

- **方式 2：使用 SSH 密钥**
  ```bash
  # 生成 SSH 密钥
  ssh-keygen -t ed25519 -C "your_email@example.com"

  # 添加到 SSH agent
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/id_ed25519

  # 复制公钥
  cat ~/.ssh/id_ed25519.pub

  # 添加到 GitHub: Settings → SSH and GPG keys → New SSH key

  # 使用 SSH URL
  git remote set-url origin git@github.com:YOUR_USERNAME/digital-heritage-platform.git
  git push -u origin main
  ```

---

### 步骤 3：在 Render 创建 Web 服务

#### 3.1 登录 Render

1. 访问 [https://dashboard.render.com](https://dashboard.render.com)
2. 点击 **"Sign Up"** 或 **"Log In"**
3. 使用 **GitHub 账号**登录并授权

#### 3.2 创建新的 Web Service

1. 点击右上角的 **"+ New"** 按钮
2. 选择 **"Web Service"**

#### 3.3 配置 Web Service

##### **基本信息**

| 配置项 | 值 |
|--------|-----|
| **Name** | `digital-heritage-platform` |
| **Region** | `Oregon (US West)` 或选择离你最近的区域 |
| **Branch** | `main` |

##### **连接 GitHub 仓库**

1. 点击 **"Connect GitHub"**（如果还没连接）
2. 授权 Render 访问你的 GitHub
3. 在 **"Connect a repository"** 下拉菜单中选择：
   - 搜索 `digital-heritage-platform`
   - 选择你的仓库
   - 点击 **"Connect"**

##### **运行时配置**

| 配置项 | 值 |
|--------|-----|
| **Runtime** | `Python` |
| **Build Command** | `apt-get update && apt-get install -y fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei && pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

**Build Command 说明：**
- `apt-get update` - 更新包列表
- `apt-get install -y fonts-noto-cjk` - 安装 Google Noto Sans CJK 中文字体
- `apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei` - 安装文泉驿中文字体（备用）
- `pip install -r requirements.txt` - 安装 Python 依赖

##### **环境变量**

点击 **"Advanced"** → **"Add Environment Variable"**

| Key | Value | 说明 |
|-----|-------|------|
| `FLASK_ENV` | `production` | 运行环境 |
| `SECRET_KEY` | `your-random-secret-key` | Flask 密钥（见下方生成方法） |
| `DATABASE_URL` | （可选）见数据库配置 | PostgreSQL 连接字符串 |

**生成 SECRET_KEY：**
```bash
# 在本地运行
python -c "import secrets; print(secrets.token_hex(32))"
```
复制生成的随机字符串作为 `SECRET_KEY` 的值。

##### **磁盘存储（可选但推荐）**

点击 **"Advanced"** → **"Add Disk"**

| 配置项 | 值 |
|--------|-----|
| **Name** | `data` |
| **Size** | `1 GB` |
| **Mount Path** | `/opt/render/project/data` |

**说明：**
- 磁盘存储用于持久化 PDF 文件和数据库
- Render 免费版每月 $2/GB
- 如果不配置，重启后数据会丢失

#### 3.4 部署

1. 检查所有配置无误
2. 点击底部的 **"Create Web Service"** 按钮
3. 等待构建和部署完成（首次约 3-5 分钟）

---

### 步骤 4：监控部署进度

#### 查看部署状态

在 Render Dashboard 中：

1. 点击你的 Web Service
2. 查看 **"Status"** 标签：
   - 🟢 **Live** - 部署成功
   - 🟡 **Building** - 正在构建
   - 🔴 **Failed** - 部署失败

#### 查看构建日志

1. 点击 **"Logs"** 标签
2. 选择 **"Build Logs"**
3. 查看详细构建过程

**成功的日志应该包含：**
```
✓ Successfully registered system font: /usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc
✓ Installing dependencies from requirements.txt
✓ Build completed successfully
```

#### 访问应用

1. 部署成功后，顶部会显示访问 URL
2. 格式：`https://digital-heritage-platform.onrender.com`
3. 点击链接访问你的应用

---

## 🔍 验证部署

### 验证清单

部署完成后，请验证以下功能：

- [ ] **首页加载**: 访问 URL，首页正常显示
- [ ] **用户注册**: 能够创建新账号
- [ ] **用户登录**: 能够登录账号
- [ ] **创建遗嘱**: 能够创建包含中文的遗嘱
- [ ] **生成 PDF**: PDF 能正确生成
- [ ] **中文显示**: PDF 中的中文正确显示（不是方框）

### 测试 PDF 中文支持

1. 登录应用
2. 创建一个新遗嘱，包含中文内容
3. 点击"生成 PDF"按钮
4. 下载并打开 PDF 文件
5. 验证中文是否正确显示

---

## 🐛 常见问题

### 问题 1：推送代码时提示 "Permission denied"

**解决方案：**
- 检查 GitHub 用户名是否正确
- 使用 Personal Access Token 代替密码
- 确保仓库权限设置正确

### 问题 2：Render 找不到仓库

**解决方案：**
- 确保 GitHub 仓库是 Public 或已授权 Render 访问
- 检查仓库名称是否正确
- 重新连接 GitHub 账号

### 问题 3：构建失败 - 字体安装错误

**错误信息：**
```
E: Unable to locate package fonts-noto-cjk
```

**解决方案：**
修改 Build Command，去掉 `fonts-noto-cjk`：
```
apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei && pip install -r requirements.txt
```

### 问题 4：部署成功但无法访问

**解决方案：**
1. 检查 Start Command 是否正确：`gunicorn app:app`
2. 查看 Runtime Logs 查找错误
3. 确保端口配置正确（默认 5000）

### 问题 5：PDF 中文显示为方框

**解决方案：**
1. 在 Render Dashboard 打开 Shell
2. 检查字体是否安装：
   ```bash
   fc-list | grep -i "wqy\|noto"
   ```
3. 如果字体未安装，手动安装：
   ```bash
   apt-get update
   apt-get install -y fonts-noto-cjk
   fc-cache -fv
   ```
4. 重启服务

---

## 📝 下一步操作

部署成功后，你可以：

1. **配置自定义域名**
   - Web Service → Settings → Custom Domains

2. **设置数据库**
   - 推荐：使用 Supabase PostgreSQL（免费）
   - 见 `RENDER_DEPLOYMENT_TUTORIAL.md` 的数据库配置章节

3. **监控应用**
   - 查看 Metrics 和 Logs
   - 配置错误监控（如 Sentry）

4. **优化性能**
   - 升级到付费计划避免休眠
   - 配置 CDN 加速

5. **定期备份**
   - 配置数据库自动备份
   - 备份重要文件

---

## 🎉 完成！

恭喜！你的数字遗产继承平台已成功部署到 Render。

**访问地址：** `https://digital-heritage-platform.onrender.com`

**需要帮助？**
- 查看 `RENDER_DEPLOYMENT_TUTORIAL.md` 获取更多详细信息
- 查看 Render 文档：[https://render.com/docs](https://render.com/docs)
- 查看 GitHub Issues

---

*最后更新：2026-02-14*
