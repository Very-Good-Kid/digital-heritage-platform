# 部署指南

## 本地开发环境部署

### 1. 环境准备
- Python 3.8 或更高版本
- pip 包管理器
- Git（可选）

### 2. 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd demo
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行测试**
   ```bash
   python test_app.py
   ```

5. **启动应用**
   ```bash
   python app.py
   ```

6. **访问应用**
   打开浏览器访问：`http://localhost:5000`

### 3. 配置说明

#### 基本配置（config.py）

```python
class Config:
    SECRET_KEY = 'your-secret-key-here'  # 生产环境必须更改
    SQLALCHEMY_DATABASE_URI = 'sqlite:///digital_heritage.db'  # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
```

#### 数据库配置

**SQLite（开发环境）**
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///digital_heritage.db'
```

**MySQL（生产环境）**
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/dbname'
```

**PostgreSQL（生产环境）**
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/dbname'
```

#### 加密密钥配置

在生产环境中，必须设置加密密钥：

```bash
# Windows
set ENCRYPTION_KEY=your-encryption-key-here

# Linux/Mac
export ENCRYPTION_KEY=your-encryption-key-here
```

或创建 `.env` 文件：
```
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
DATABASE_URL=sqlite:///digital_heritage.db
```

## 生产环境部署

### 1. 使用 Gunicorn（推荐）

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. 使用 uWSGI

```bash
pip install uwsgi

uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

### 3. 使用 Docker

创建 `Dockerfile`：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

创建 `docker-compose.yml`：
```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=your-secret-key
      - ENCRYPTION_KEY=your-encryption-key
    volumes:
      - ./data:/app/data
```

运行：
```bash
docker-compose up -d
```

### 4. 使用 Nginx 反向代理

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/your/app/static;
    }
}
```

## 安全配置

### 1. HTTPS 配置

使用 Let's Encrypt 免费证书：
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 防火墙配置

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. 数据库备份

创建备份脚本 `backup.sh`：
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# SQLite 备份
cp digital_heritage.db $BACKUP_DIR/digital_heritage_$DATE.db

# MySQL 备份
# mysqldump -u username -p dbname > $BACKUP_DIR/backup_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
```

设置定时任务：
```bash
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

## 监控和日志

### 1. 应用日志

在 `app.py` 中添加日志配置：
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 性能监控

使用 Prometheus + Grafana：
```bash
pip install prometheus_flask_exporter
```

### 3. 错误追踪

使用 Sentry：
```bash
pip install sentry-sdk
```

## 常见问题

### 1. 端口被占用
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### 2. 数据库连接失败
- 检查数据库服务是否启动
- 验证连接字符串配置
- 确认数据库用户权限

### 3. 文件上传失败
- 检查上传目录权限
- 确认文件大小限制配置
- 验证磁盘空间

## 性能优化

### 1. 数据库优化
- 添加适当的索引
- 使用连接池
- 定期清理过期数据

### 2. 缓存配置
```bash
pip install redis flask-caching
```

### 3. 静态文件优化
- 使用 CDN
- 启用 gzip 压缩
- 合并和压缩 CSS/JS 文件

## 维护建议

1. **定期更新依赖**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

2. **安全扫描**
   ```bash
   pip install safety
   safety check
   ```

3. **代码质量检查**
   ```bash
   pip install flake8 black
   flake8 .
   black .
   ```

4. **定期备份数据**
   - 每日自动备份数据库
   - 保留至少30天的备份
   - 测试恢复流程

## 联系支持

如有问题，请联系：
- 邮箱：support@digitalheritage.com
- 文档：https://docs.digitalheritage.com
