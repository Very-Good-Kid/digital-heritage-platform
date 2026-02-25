# -*- coding: utf-8 -*-
"""
Render 部署初始化脚本
用于在 Render 上初始化数据库并同步 FAQ 数据
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text

def check_environment():
    """检查环境变量"""
    print("=" * 60)
    print("检查环境配置...")
    print("=" * 60)

    database_url = os.environ.get('DATABASE_URL')
    secret_key = os.environ.get('SECRET_KEY')
    flask_env = os.environ.get('FLASK_ENV', 'production')

    checks = []

    # 检查 DATABASE_URL
    if database_url:
        # 隐藏密码
        masked_url = database_url.split('@')[0].split('//')[1][:5] + '***@' + database_url.split('@')[1]
        print(f"✅ DATABASE_URL: {masked_url}")
        checks.append(True)
    else:
        print("❌ DATABASE_URL: 未设置")
        checks.append(False)

    # 检查 SECRET_KEY
    if secret_key and secret_key != 'your-secret-key-change-this-in-production':
        print(f"✅ SECRET_KEY: 已设置 (长度: {len(secret_key)})")
        checks.append(True)
    else:
        print("⚠️  SECRET_KEY: 使用默认值，建议修改")
        checks.append(True)  # 不阻止部署，只是警告

    # 检查 FLASK_ENV
    print(f"✅ FLASK_ENV: {flask_env}")
    checks.append(True)

    return all(checks)

def init_database():
    """初始化数据库表"""
    print("\n" + "=" * 60)
    print("初始化数据库表...")
    print("=" * 60)

    try:
        from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ, PolicyDetail
        from app import app

        with app.app_context():
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")

            # 检查是否需要初始化管理员
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count == 0:
                print("\n⚠️  未检测到管理员账号")
                print("   请使用 create_admin.py 创建管理员账号")
            else:
                print(f"✅ 已存在 {admin_count} 个管理员账号")

            # 检查 FAQ 数据
            faq_count = FAQ.query.count()
            print(f"✅ FAQ 数据: {faq_count} 条")

            # 检查平台政策
            policy_count = PlatformPolicy.query.count()
            print(f"✅ 平台政策: {policy_count} 条")

            return True

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def sync_faq_from_local():
    """
    从本地 SQLite 同步 FAQ 到 Neon PostgreSQL
    注意：此功能仅在本地执行，用于准备同步数据
    """
    print("\n" + "=" * 60)
    print("FAQ 数据同步")
    print("=" * 60)

    # 检查是否在本地环境
    if os.environ.get('FLASK_ENV') == 'development':
        print("⚠️  当前为开发环境")
        print("   如需同步 FAQ 到 Render，请运行: python sync_faq_to_neon.py")
        return True

    # 生产环境不执行此操作
    print("ℹ️  生产环境不需要执行此操作")
    print("   请在本地运行 sync_faq_to_neon.py 进行同步")
    return True

def verify_sync():
    """验证同步结果"""
    print("\n" + "=" * 60)
    print("验证数据同步...")
    print("=" * 60)

    try:
        from models import db, FAQ
        from app import app

        with app.app_context():
            faq_count = FAQ.query.count()

            if faq_count > 0:
                print(f"✅ FAQ 数据验证成功: {faq_count} 条")

                # 显示前 3 条 FAQ
                faqs = FAQ.query.order_by(FAQ.order).limit(3).all()
                print("\n示例 FAQ:")
                for faq in faqs:
                    print(f"   - [{faq.order}] {faq.question[:50]}...")

                return True
            else:
                print("⚠️  FAQ 数据为空")
                print("   请在本地运行: python sync_faq_to_neon.py")
                return False

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Render 部署初始化")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"环境: {os.environ.get('FLASK_ENV', 'production')}")

    # 1. 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请检查配置")
        sys.exit(1)

    # 2. 初始化数据库
    if not init_database():
        print("\n❌ 数据库初始化失败")
        sys.exit(1)

    # 3. FAQ 同步提示
    sync_faq_from_local()

    # 4. 验证同步
    verify_sync()

    print("\n" + "=" * 60)
    print("✅ 初始化完成!")
    print("=" * 60)
    print("\n后续步骤:")
    print("1. 如果是首次部署，请创建管理员账号:")
    print("   python create_admin.py")
    print("\n2. 如果需要同步 FAQ 数据，请在本地运行:")
    print("   python sync_faq_to_neon.py")
    print("\n3. 访问管理员后台:")
    print("   https://your-app.onrender.com/admin")
    print("=" * 60)

if __name__ == '__main__':
    main()
