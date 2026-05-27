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
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    daily_chat_limit = db.Column(db.Integer, default=5)  # 每日AI对话次数限制，默认5次
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


class KnowledgeFile(db.Model):
    """知识库文件模型 - 存储用户上传的知识库源文件"""
    __tablename__ = 'knowledge_files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    file_type = db.Column(db.String(20), nullable=False)   # 文件类型: pdf/txt/md/docx
    file_data = db.Column(db.LargeBinary)                   # 文件二进制数据(存入DB,避免Render磁盘丢失)
    chunk_count = db.Column(db.Integer, default=0)          # 切分后的文本块数量
    created_at = db.Column(db.DateTime, default=get_china_time)

    # 关系: 一个文件对应多个文本块
    chunks = db.relationship('KnowledgeChunk', backref='source_file', lazy='dynamic',
                             cascade='all, delete-orphan')

    def __repr__(self):
        return f'<KnowledgeFile {self.filename}>'


class KnowledgeChunk(db.Model):
    """知识库文本块模型 - 存储切分后的文本片段及其向量"""
    __tablename__ = 'knowledge_chunks'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('knowledge_files.id'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)     # 在源文件中的块序号
    content = db.Column(db.Text, nullable=False)             # 原文内容
    embedding = db.Column(db.Text, nullable=True)            # 向量数据(JSON格式存储的浮点数组)
    created_at = db.Column(db.DateTime, default=get_china_time)

    def __repr__(self):
        return f'<KnowledgeChunk file_id={self.file_id} idx={self.chunk_index}>'


class ChatMessage(db.Model):
    """对话消息模型 - 存储AI对话的聊天记录"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_china_time)

    def __repr__(self):
        return f'<ChatMessage {self.role} session={self.session_id}>'


class ChatUsage(db.Model):
    """对话使用量模型 - 记录每位用户每日的AI对话次数"""
    __tablename__ = 'chat_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    usage_date = db.Column(db.String(10), nullable=False, index=True)  # 日期格式 YYYY-MM-DD
    count = db.Column(db.Integer, default=0)                            # 当日已使用次数
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)

    # 同一用户同一天唯一
    __table_args__ = (db.UniqueConstraint('user_id', 'usage_date', name='uq_user_date'),)

    def __repr__(self):
        return f'<ChatUsage user={self.user_id} date={self.usage_date} count={self.count}>'
