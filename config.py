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
    
    # 会话配置 - 确保在部署环境中持久化
    SESSION_COOKIE_SECURE = False  # 开发环境为False，生产环境根据需要设置
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = True

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

    # 生产环境优先使用Supabase PostgreSQL（免费且持久化）
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        # 修复PostgreSQL连接字符串格式
        # 将 postgres:// 替换为 postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

        # 添加SSL和连接池参数以提高性能和稳定性
        # Neon数据库需要SSL连接
        # 优化连接池配置
        if '?' in DATABASE_URL:
            DATABASE_URL += '&sslmode=require&pool_pre_ping=True&pool_size=10&max_overflow=20&pool_recycle=1800&pool_timeout=30'
        else:
            DATABASE_URL += '?sslmode=require&pool_pre_ping=True&pool_size=10&max_overflow=20&pool_recycle=1800&pool_timeout=30'

        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"✅ 使用外部PostgreSQL数据库: {DATABASE_URL.split('@')[0]}@...")
    else:
        # 如果没有提供DATABASE_URL，使用SQLite（不推荐用于生产）
        DATA_DIR = os.environ.get('RENDER_DATA_DIR') or '/opt/render/project/data'
        db_path = os.path.join(DATA_DIR, 'digital_heritage.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        print("⚠️  警告: 生产环境使用SQLite，数据可能丢失！建议配置Supabase PostgreSQL。")

    # 上传文件夹使用临时目录（Render免费版）
    UPLOAD_FOLDER = '/tmp/uploads'

    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        except:
            pass

    # 生产环境会话配置
    SESSION_COOKIE_SECURE = True  # 生产环境使用HTTPS时设置为True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = True

    # 确保SECRET_KEY在环境中设置
    if not os.environ.get('SECRET_KEY'):
        print("⚠️  警告: 生产环境未设置SECRET_KEY环境变量！")
        print("    请在 Render 环境变量中设置 SECRET_KEY")

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
