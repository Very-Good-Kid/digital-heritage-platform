# 数字资产继承平台 - Render云服务部署指南

## 一、为什么选择Render？

### 优势：
- ✅ **完全免费**：免费套餐包含512MB RAM、0.1 CPU
- ✅ **自动部署**：连接GitHub后自动部署
- ✅ **HTTPS支持**：自动配置SSL证书
- ✅ **持久化存储**：提供免费的磁盘持久化
- ✅ **全球CDN**：快速访问体验
- ✅ **简单易用**：无需复杂配置

### 免费套餐限制：
- 内存：512MB
- CPU：0.1核
- 每月运行时间：750小时
- 磁盘空间：100MB（持久化存储）

---

## 二、部署前准备工作

### 2.1 准备GitHub仓库

1. **创建GitHub仓库**
   ```bash
   # 在GitHub上创建新仓库
   # 仓库名：digital-heritage-platform
   ```

2. **初始化本地Git仓库**
   ```bash
   cd c:\Users\admin\Desktop\demo - codebuddy
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **连接远程仓库**
   ```bash
   git remote add origin https://github.com/你的用户名/digital-heritage-platform.git
   git branch -M main
   git push -u origin main
   ```

### 2.2 准备项目文件

确保项目包含以下文件：

```
demo - codebuddy/
├── app.py                      # 主应用文件
├── config.py                   # 配置文件
├── models.py                   # 数据库模型
├── requirements.txt            # Python依赖
├── Procfile                    # Render启动配置
├── runtime.txt                 # Python版本
└── .gitignore                  # Git忽略文件
```

---

## 三、详细部署流程

### 3.1 注册Render账号

1. 访问 [https://render.com](https://render.com)
2. 点击 "Sign Up" 注册账号
3. 使用GitHub账号登录（推荐）

### 3.2 创建Web服务

1. **登录Render后端**
   - 点击 "New +" 按钮
   - 选择 "Web Service"

2. **连接GitHub仓库**
   - 选择您的 `digital-heritage-platform` 仓库
   - 点击 "Connect"

3. **配置服务信息**

   **基本信息：**
   - Name: `digital-heritage-platform`
   - Region: `Singapore`（选择离您最近的区域）
   - Branch: `main`

   **运行环境：**
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **环境变量配置**

   点击 "Advanced" → "Environment Variables"，添加以下变量：

   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   `FLASK_ENV` | `production` | 生产环境模式 |
   `SECRET_KEY` | `your-secret-key-here` | 随机生成的密钥 |
   `DATABASE_URL` | `sqlite:///instance/digital_heritage.db` | 数据库路径 |

   **生成SECRET_KEY：**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

5. **选择套餐**
   - 选择 "Free" 免费套餐

6. **创建服务**
   - 点击 "Create Web Service"
   - 等待部署完成（约5-10分钟）

### 3.3 配置数据库持久化（重要！）

Render免费套餐的磁盘在重启后会清空，需要配置持久化存储：

1. **修改config.py**
   ```python
   import os
   from datetime import timedelta

   class ProductionConfig(Config):
       """生产环境配置"""
       DEBUG = False
       # 使用持久化目录
       DATA_DIR = os.environ.get('RENDER_DATA_DIR', '/opt/render/project/data')
       os.makedirs(DATA_DIR, exist_ok=True)

       # 数据库路径
       db_path = os.path.join(DATA_DIR, 'digital_heritage.db')
       SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
       SQLALCHEMY_TRACK_MODIFICATIONS = False
       PERMANENT_SESSION_LIFETIME = timedelta(days=7)
       MAX_CONTENT_LENGTH = 16 * 1024 * 1024
       UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
       ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
   ```

2. **上传修改后的文件到GitHub**
   ```bash
   git add config.py
   git commit -m "Update config for persistent storage"
   git push
   ```

3. **Render会自动重新部署**

---

## 四、启动命令和端口配置

### 4.1 Procfile配置

创建 `Procfile` 文件（项目根目录）：

```procfile
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
```

**参数说明：**
- `--bind 0.0.0.0:$PORT`：绑定到Render指定的端口
- `--workers 1`：工作进程数（免费套餐建议1个）
- `--threads 2`：每个进程的线程数
- `--timeout 120`：请求超时时间（秒）

### 4.2 runtime.txt配置

创建 `runtime.txt` 文件（项目根目录）：

```
python-3.11.7
```

### 4.3 修改app.py以支持端口配置

在app.py的最后，修改启动方式：

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 4.4 本地启动命令

**开发环境：**
```bash
# Windows
python app.py

# 或使用虚拟环境
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**生产环境（Render）：**
- Render会自动执行 `gunicorn app:app` 启动应用

---

## 五、域名访问方式

### 5.1 默认访问地址

部署成功后，Render会提供默认地址：
```
https://digital-heritage-platform.onrender.com
```

### 5.2 自定义域名配置（可选）

1. **购买域名**
   - 推荐使用阿里云、腾讯云、Namecheap等

2. **在Render中添加自定义域名**
   - 进入Web Service设置
   - 点击 "Custom Domains"
   - 添加您的域名（如：`www.yourdomain.com`）

3. **配置DNS**
   - 登录域名注册商
   - 添加CNAME记录：
     ```
     类型: CNAME
     主机记录: www
     记录值: digital-heritage-platform.onrender.com
     ```

4. **等待DNS生效**
   - 通常需要10分钟到24小时

5. **HTTPS自动配置**
   - Render会自动为自定义域名配置SSL证书

---

## 六、数据库管理

### 6.1 初始化数据库

首次部署后，需要初始化数据库：

1. **访问应用**
   ```
   https://digital-heritage-platform.onrender.com
   ```

2. **应用会自动初始化数据库**
   - 首次访问时，`initialize_database()` 函数会自动执行
   - 创建所有数据表
   - 插入示例数据

### 6.2 创建管理员账户

使用提供的脚本创建管理员：

```bash
# 在本地运行（需要配置远程数据库连接）
python create_admin.py
```

或通过注册页面注册后，手动修改数据库：

```python
# 进入Python REPL
python

# 执行以下代码
from app import app, db, User
with app.app_context():
    user = User.query.filter_by(username='your_username').first()
    user.is_admin = True
    db.session.commit()
```

---

## 七、监控和维护

### 7.1 查看日志

1. **在Render中查看日志**
   - 进入Web Service
   - 点击 "Logs"
   - 实时查看应用日志

2. **常见日志信息**
   - 应用启动/重启
   - 错误信息
   - 用户访问记录

### 7.2 性能监控

Render免费套餐提供：
- CPU使用率
- 内存使用情况
- 响应时间
- 请求成功率

### 7.3 自动重启

如果应用崩溃，Render会自动重启。

---

## 八、故障排查

### 8.1 部署失败

**问题：** 部署时出现错误

**解决方案：**
1. 检查 `requirements.txt` 是否完整
2. 确保Python版本兼容
3. 查看部署日志定位错误

### 8.2 数据库丢失

**问题：** 重启后数据丢失

**解决方案：**
1. 确保配置了持久化存储
2. 检查 `RENDER_DATA_DIR` 环境变量
3. 使用外部数据库（可选）

### 8.3 内存不足

**问题：** 应用因内存不足崩溃

**解决方案：**
1. 优化数据库查询
2. 减少并发连接
3. 升级到付费套餐

---

## 九、升级方案

如果免费套餐不够用，可以考虑：

### 9.1 Render付费套餐

| 套餐 | 内存 | CPU | 价格 |
|------|------|-----|------|
| Starter | 512MB | 0.5 | $7/月 |
| Standard | 2GB | 1 | $25/月 |
| Pro | 8GB | 4 | $100/月 |

### 9.2 使用外部数据库

- PostgreSQL免费套餐：Supabase、Neon
- 更好的性能和可靠性
- 数据不会丢失

---

## 十、安全建议

1. **定期更新依赖**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **设置强SECRET_KEY**
   - 使用随机生成的密钥
   - 不要在代码中硬编码

3. **启用HTTPS**
   - Render自动配置
   - 强制使用HTTPS

4. **定期备份数据**
   - 导出数据库
   - 保存到安全位置

---

## 十一、快速启动命令总结

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 访问地址
http://localhost:5000
```

### Render部署
```bash
# 推送代码到GitHub
git add .
git commit -m "Update"
git push

# Render自动部署
# 访问地址
https://digital-heritage-platform.onrender.com
```

### 创建管理员
```bash
# 运行创建脚本
python create_admin.py
```

---

## 十二、联系方式

如有问题，请联系：
- Render文档：https://render.com/docs
- Flask文档：https://flask.palletsprojects.com/

---

**祝您部署成功！** 🎉
