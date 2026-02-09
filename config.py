import os
from datetime import timedelta

class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///digital_heritage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 使用环境变量获取数据库URL，Render会自动设置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///digital_heritage.db'
    # 确保SQLite URL格式正确
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('sqlite://', 'sqlite:///')

    # 确保数据目录存在
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    # 使用 Render 的持久化磁盘
    DATA_DIR = os.environ.get('RENDER_DATA_DIR') or '/opt/render/project/data'
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 根据环境变量自动选择配置
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    default_config = config['production']
else:
    default_config = config['default']

config['default'] = default_config
