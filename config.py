import os
from datetime import timedelta

class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

    # 数据持久化目录 - 使用绝对路径
    DATA_DIR = os.path.abspath('instance')

    # 开发环境使用本地数据库 - 使用绝对路径
    # SQLite URI格式：sqlite:///path/to/database.db (3个斜杠，即使对于绝对路径)
    db_path = os.path.join(DATA_DIR, 'digital_heritage.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

    # 使用 Render 的持久化磁盘
    DATA_DIR = os.environ.get('RENDER_DATA_DIR') or '/opt/render/project/data'

    # 数据库文件存储在持久化目录
    db_path = os.path.join(DATA_DIR, 'digital_heritage.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'

    # 上传文件夹也使用持久化目录
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')

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
