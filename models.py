from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 时区设置：中国标准时间 (UTC+8)
TIMEZONE_OFFSET = timedelta(hours=8)

def get_china_time():
    """获取中国标准时间"""
    return datetime.utcnow() + TIMEZONE_OFFSET

def format_china_time(dt):
    """格式化中国标准时间显示"""
    if dt is None:
        return ''
    # 如果已经是UTC时间，转换为中国时间
    china_time = dt + TIMEZONE_OFFSET
    return china_time.strftime('%Y-%m-%d %H:%M:%S')

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    # 关系
    digital_assets = db.relationship('DigitalAsset', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    digital_wills = db.relationship('DigitalWill', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class DigitalAsset(db.Model):
    """数字资产模型"""
    __tablename__ = 'digital_assets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    platform_name = db.Column(db.String(100), nullable=False)
    account = db.Column(db.String(200), nullable=False)
    encrypted_password = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)  # 社交媒体、电子邮箱、云存储与数字内容、虚拟资产与数字货币、其他数字资产
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_china_time, index=True)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    def __repr__(self):
        return f'<DigitalAsset {self.platform_name}>'

class DigitalWill(db.Model):
    """数字资产处置意愿声明书模型"""
    __tablename__ = 'digital_wills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assets_data = db.Column(db.JSON)  # 存储资产处理选项
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, archived
    created_at = db.Column(db.DateTime, default=get_china_time, index=True)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    def __repr__(self):
        return f'<DigitalWill {self.title}>'

class PlatformPolicy(db.Model):
    """平台政策模型"""
    __tablename__ = 'platform_policies'

    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    policy_content = db.Column(db.Text, nullable=False)
    attitude = db.Column(db.String(50), nullable=False)  # 明确禁止、态度模糊、有限支持、主动服务
    inherit_possibility = db.Column(db.String(10), nullable=False)  # 低、中、高
    legal_basis = db.Column(db.Text)
    customer_service = db.Column(db.String(500))  # 扩展长度以支持多个联系方式
    risk_warning = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)
    
    # 关联政策条款详情
    policy_details = db.relationship('PolicyDetail', backref='platform', lazy='dynamic', 
                                     cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PlatformPolicy {self.platform_name}>'


class PolicyDetail(db.Model):
    """政策条款详情模型 - 用于存储二、主流平台相关政策收集的内容"""
    __tablename__ = 'policy_details'

    id = db.Column(db.Integer, primary_key=True)
    platform_policy_id = db.Column(db.Integer, db.ForeignKey('platform_policies.id'), nullable=False)
    policy_title = db.Column(db.String(200), nullable=False)  # 政策条款标题
    policy_text = db.Column(db.Text, nullable=False)  # 政策条款原文
    legal_interpretation = db.Column(db.Text)  # 法律解读
    display_order = db.Column(db.Integer, default=0)  # 显示顺序
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    def __repr__(self):
        return f'<PolicyDetail {self.policy_title}>'


class Story(db.Model):
    """故事模型"""
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    category = db.Column(db.String(50))  # 个人分享，官方发布
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    def __repr__(self):
        return f'<Story {self.title}>'

class FAQ(db.Model):
    """FAQ模型"""
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    def __repr__(self):
        return f'<FAQ {self.question}>'
