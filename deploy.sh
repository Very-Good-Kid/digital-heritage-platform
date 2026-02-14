#!/bin/bash
# Lighthouse服务器部署脚本

set -e

echo "开始部署..."

# 创建项目目录
mkdir -p /root/demo-codebuddy
cd /root/demo-codebuddy

# 创建必要的目录
mkdir -p instance uploads static/uploads temp_pdfs

# 创建requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Werkzeug==3.0.1
gunicorn>=21.0.0
cryptography>=41.0.0
reportlab>=4.0.0
Pillow>=10.4.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
email-validator>=2.0.0
WTForms>=3.0.0
EOF

# 创建简单的app.py
cat > app.py << 'EOF'
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Demo应用已成功部署到Lighthouse！"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# 构建Docker镜像
echo "构建Docker镜像..."
docker build -t demo-codebuddy:latest .

# 停止旧容器（如果存在）
echo "停止旧容器..."
docker stop demo-codebuddy 2>/dev/null || true
docker rm demo-codebuddy 2>/dev/null || true

# 启动新容器
echo "启动新容器..."
docker run -d \
  --name demo-codebuddy \
  --restart=unless-stopped \
  -p 5000:5000 \
  -v /root/demo-codebuddy/instance:/app/instance \
  -v /root/demo-codebuddy/uploads:/app/uploads \
  -v /root/demo-codebuddy/temp_pdfs:/app/temp_pdfs \
  demo-codebuddy:latest

echo "部署完成！"
echo "应用访问地址: http://111.229.242.108:5000"
