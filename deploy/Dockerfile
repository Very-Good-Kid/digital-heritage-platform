FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖（使用官方PyPI，避免供应链风险）
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（依赖仓库根目录的 .dockerignore 排除敏感文件）
COPY . .

# 创建必要目录
RUN mkdir -p instance uploads static/uploads temp_pdfs

# 安全：添加非 root 用户
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 生产用 gunicorn（绝不使用 python app.py debug 模式）
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "app:app"]
