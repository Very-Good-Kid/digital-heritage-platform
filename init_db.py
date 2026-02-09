#!/usr/bin/env python3
"""
数据库初始化脚本
在 Render 部署时自动运行，确保数据库和必要目录存在
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建成功")

        # 检查并初始化示例数据
        init_sample_data()
        print("✓ 示例数据初始化完成")

def init_sample_data():
    """初始化示例数据"""
    # 检查是否已有平台政策数据
    if PlatformPolicy.query.count() == 0:
        print("正在添加平台政策数据...")
        policies = [
            PlatformPolicy(
                platform_name='微信',
                policy_content='微信账户不支持继承，账户长期不使用会被冻结。',
                attitude='明确禁止',
                inherit_possibility='低',
                legal_basis='根据《微信软件许可及服务协议》，用户仅拥有使用权，不拥有所有权',
                customer_service='400-670-0700',
                risk_warning='账户余额可能无法提取，聊天记录可能永久丢失'
            ),
            PlatformPolicy(
                platform_name='QQ',
                policy_content='QQ号码可以申请继承，需要提供相关证明材料。',
                attitude='有限支持',
                inherit_possibility='中',
                legal_basis='腾讯提供账户继承服务，但需要严格的法律文件',
                customer_service='0755-83765566',
                risk_warning='需要提供完整的法律证明文件，审核周期较长'
            ),
            PlatformPolicy(
                platform_name='抖音',
                policy_content='抖音账号继承政策尚不明确，建议联系客服咨询。',
                attitude='态度模糊',
                inherit_possibility='低',
                legal_basis='相关政策尚未明确规定',
                customer_service='400-966-0606',
                risk_warning='继承成功率较低，建议提前做好数据备份'
            )
        ]

        for policy in policies:
            db.session.add(policy)
        db.session.commit()
        print("✓ 平台政策数据添加成功")

    # 检查是否已有FAQ数据
    if FAQ.query.count() == 0:
        print("正在添加FAQ数据...")
        faqs = [
            FAQ(
                question='数字遗产包括哪些内容？',
                answer='数字遗产包括但不限于：社交媒体账号（微信、QQ、抖音等）、电子邮箱、云存储文件、虚拟货币、游戏账号、在线支付账户等。',
                category='基础概念',
                order=1
            ),
            FAQ(
                question='如何保护我的数字遗产？',
                answer='1. 定期备份重要数据；2. 使用密码管理器；3. 创建数字遗嘱；4. 告知家人重要账户信息；5. 了解各平台的继承政策。',
                category='保护措施',
                order=2
            ),
            FAQ(
                question='数字遗嘱有法律效力吗？',
                answer='数字遗嘱在我国法律体系中尚未明确认定，但可以作为表达意愿的重要依据。建议配合传统遗嘱使用，并咨询专业律师。',
                category='法律问题',
                order=3
            )
        ]

        for faq in faqs:
            db.session.add(faq)
        db.session.commit()
        print("✓ FAQ数据添加成功")

    # 检查是否已有故事数据
    if Story.query.count() == 0:
        print("正在添加故事数据...")
        stories = [
            Story(
                title='父亲的微信账号',
                content='父亲去世后，我尝试找回他的微信账号，却遇到了重重困难。这让我意识到数字遗产规划的重要性...',
                author='匿名用户',
                category='情感故事',
                status='approved'
            ),
            Story(
                title='数字时代的告别',
                content='在这个数字时代，我们的记忆、情感都存储在云端。如何让这些珍贵的数字遗产得以延续？',
                author='编辑部',
                category='哲思文章',
                status='approved'
            )
        ]

        for story in stories:
            db.session.add(story)
        db.session.commit()
        print("✓ 故事数据添加成功")

def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        'uploads',
        'static/uploads',
        'temp_pdfs',
        'data'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✓ 创建目录: {directory}")

if __name__ == '__main__':
    print("=" * 50)
    print("数字遗产继承平台 - 数据库初始化")
    print("=" * 50)
    print()

    # 确保目录存在
    ensure_directories()
    print()

    # 初始化数据库
    try:
        init_database()
        print()
        print("=" * 50)
        print("✓ 数据库初始化完成！")
        print("=" * 50)
    except Exception as e:
        print()
        print("=" * 50)
        print(f"✗ 数据库初始化失败: {e}")
        print("=" * 50)
        sys.exit(1)
