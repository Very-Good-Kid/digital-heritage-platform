"""
将本地SQLite数据库数据同步到Neon PostgreSQL数据库
"""
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import os
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

print("=" * 60)
print("本地SQLite → Neon PostgreSQL 数据同步")
print("=" * 60)

# 检查DATABASE_URL
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("\n❌ 错误: 未设置DATABASE_URL环境变量")
    print("\n请按以下步骤操作:")
    print("  1. 打开 .env 文件")
    print("  2. 将 DATABASE_URL 设置为您的Neon数据库连接字符串")
    print("  3. 格式: postgres://user:password@host/database?sslmode=require")
    print("  4. 保存文件后重新运行此脚本")
    exit(1)

print(f"\n✅ 检测到Neon数据库配置")

try:
    from sqlalchemy import create_engine, text
    from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ
    from app import app

    # 创建SQLite引擎(本地)
    sqlite_engine = create_engine('sqlite:///instance/digital_heritage.db')

    # 创建PostgreSQL引擎(Neon)
    neon_engine = create_engine(database_url)

    print("\n" + "=" * 60)
    print("开始数据同步...")
    print("=" * 60)

    # 同步用户数据
    print("\n📊 同步用户数据...")
    with sqlite_engine.connect() as sqlite_conn:
        result = sqlite_conn.execute(text("SELECT id, username, email, password_hash, is_admin, created_at FROM user"))
        users = result.fetchall()
        print(f"   本地用户数量: {len(users)}")

    with neon_engine.connect() as neon_conn:
        for user in users:
            user_id, username, email, password_hash, is_admin, created_at = user
            # 检查是否已存在
            existing = neon_conn.execute(
                text("SELECT id FROM user WHERE id = :id"),
                {'id': user_id}
            ).fetchone()

            if existing:
                # 更新
                neon_conn.execute(text("""
                    UPDATE user
                    SET username = :username, email = :email, password_hash = :password_hash,
                        is_admin = :is_admin, created_at = :created_at
                    WHERE id = :id
                """), {
                    'id': user_id, 'username': username, 'email': email,
                    'password_hash': password_hash, 'is_admin': is_admin, 'created_at': created_at
                })
            else:
                # 插入
                neon_conn.execute(text("""
                    INSERT INTO user (id, username, email, password_hash, is_admin, created_at)
                    VALUES (:id, :username, :email, :password_hash, :is_admin, :created_at)
                """), {
                    'id': user_id, 'username': username, 'email': email,
                    'password_hash': password_hash, 'is_admin': is_admin, 'created_at': created_at
                })

        neon_conn.commit()
        print(f"   ✅ 用户数据同步完成")

    # 同步FAQ数据
    print("\n📊 同步FAQ数据...")
    with sqlite_engine.connect() as sqlite_conn:
        result = sqlite_conn.execute(text("SELECT id, question, answer, category, \"order\" FROM faq"))
        faqs = result.fetchall()
        print(f"   本地FAQ数量: {len(faqs)}")

    with neon_engine.connect() as neon_conn:
        for faq in faqs:
            faq_id, question, answer, category, order = faq
            # 检查是否已存在
            existing = neon_conn.execute(
                text("SELECT id FROM faq WHERE id = :id"),
                {'id': faq_id}
            ).fetchone()

            if existing:
                # 更新
                neon_conn.execute(text("""
                    UPDATE faq
                    SET question = :question, answer = :answer, category = :category, \"order\" = :order
                    WHERE id = :id
                """), {
                    'id': faq_id, 'question': question, 'answer': answer,
                    'category': category, 'order': order
                })
            else:
                # 插入
                neon_conn.execute(text("""
                    INSERT INTO faq (id, question, answer, category, \"order\")
                    VALUES (:id, :question, :answer, :category, :order)
                """), {
                    'id': faq_id, 'question': question, 'answer': answer,
                    'category': category, 'order': order
                })

        neon_conn.commit()
        print(f"   ✅ FAQ数据同步完成")

    # 同步资产分类数据
    print("\n📊 同步资产分类数据...")
    try:
        with sqlite_engine.connect() as sqlite_conn:
            result = sqlite_conn.execute(text("SELECT id, name, description, icon, \"order\" FROM asset_category"))
            categories = result.fetchall()
            print(f"   本地资产分类数量: {len(categories)}")

        with neon_engine.connect() as neon_conn:
            for cat in categories:
                cat_id, name, description, icon, order = cat
                # 检查是否已存在
                existing = neon_conn.execute(
                    text("SELECT id FROM asset_category WHERE id = :id"),
                    {'id': cat_id}
                ).fetchone()

                if existing:
                    # 更新
                    neon_conn.execute(text("""
                        UPDATE asset_category
                        SET name = :name, description = :description, icon = :icon, \"order\" = :order
                        WHERE id = :id
                    """), {
                        'id': cat_id, 'name': name, 'description': description,
                        'icon': icon, 'order': order
                    })
                else:
                    # 插入
                    neon_conn.execute(text("""
                        INSERT INTO asset_category (id, name, description, icon, \"order\")
                        VALUES (:id, :name, :description, :icon, :order)
                    """), {
                        'id': cat_id, 'name': name, 'description': description,
                        'icon': icon, 'order': order
                    })

            neon_conn.commit()
            print(f"   ✅ 资产分类数据同步完成")
    except Exception as e:
        print(f"   ⚠️  资产分类表不存在或同步失败: {e}")

    # 同步平台政策数据
    print("\n📊 同步平台政策数据...")
    try:
        with sqlite_engine.connect() as sqlite_conn:
            result = sqlite_conn.execute(text("""
                SELECT id, platform_name, policy_content, policy_url, last_updated
                FROM platform_policy
            """))
            policies = result.fetchall()
            print(f"   本地平台政策数量: {len(policies)}")

        with neon_engine.connect() as neon_conn:
            for policy in policies:
                policy_id, platform_name, policy_content, policy_url, last_updated = policy
                # 检查是否已存在
                existing = neon_conn.execute(
                    text("SELECT id FROM platform_policy WHERE id = :id"),
                    {'id': policy_id}
                ).fetchone()

                if existing:
                    # 更新
                    neon_conn.execute(text("""
                        UPDATE platform_policy
                        SET platform_name = :platform_name, policy_content = :policy_content,
                            policy_url = :policy_url, last_updated = :last_updated
                        WHERE id = :id
                    """), {
                        'id': policy_id, 'platform_name': platform_name,
                        'policy_content': policy_content, 'policy_url': policy_url,
                        'last_updated': last_updated
                    })
                else:
                    # 插入
                    neon_conn.execute(text("""
                        INSERT INTO platform_policy (id, platform_name, policy_content, policy_url, last_updated)
                        VALUES (:id, :platform_name, :policy_content, :policy_url, :last_updated)
                    """), {
                        'id': policy_id, 'platform_name': platform_name,
                        'policy_content': policy_content, 'policy_url': policy_url,
                        'last_updated': last_updated
                    })

            neon_conn.commit()
            print(f"   ✅ 平台政策数据同步完成")
    except Exception as e:
        print(f"   ⚠️  平台政策表不存在或同步失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 数据同步完成!")
    print("=" * 60)
    print(f"\n同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n下一步:")
    print(f"  1. 启动应用: python app.py")
    print(f"  2. 访问 http://localhost:5000")
    print(f"  3. 验证数据是否正确显示")

except Exception as e:
    print(f"\n❌ 同步失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
