"""
测试Neon数据库连接
"""
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 60)
print("Neon数据库连接测试")
print("=" * 60)

# 检查DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
print(f"\n1. 检查环境变量:")
print(f"   - DATABASE_URL已设置: {'是' if database_url else '否'}")

if database_url:
    # 隐藏密码
    masked_url = database_url.split('@')[0] + '@' + database_url.split('@')[1] if '@' in database_url else database_url
    print(f"   - 连接字符串: {masked_url}")

    # 尝试连接
    print(f"\n2. 尝试连接Neon数据库...")
    try:
        from sqlalchemy import create_engine, text
        import psycopg2

        # 创建引擎
        engine = create_engine(database_url)

        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"   ✅ 连接成功!")
            print(f"   - PostgreSQL版本: {version[:50]}...")

            # 检查现有表
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"   - 现有数据表: {len(tables)} 个")
            for table in tables:
                print(f"     • {table}")

        print(f"\n3. 测试写入权限...")
        with engine.connect() as conn:
            # 创建测试表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
            print(f"   ✅ 写入权限正常")

            # 清理测试表
            conn.execute(text("DROP TABLE IF EXISTS connection_test;"))
            conn.commit()
            print(f"   ✅ 清理完成")

        print(f"\n" + "=" * 60)
        print(f"✅ Neon数据库连接测试成功!")
        print(f"=" * 60)
        print(f"\n下一步:")
        print(f"  1. 运行 'python init_db.py' 初始化数据库结构")
        print(f"  2. 运行同步脚本迁移本地数据")

    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n" + "=" * 60)
        print(f"❌ Neon数据库连接测试失败!")
        print(f"=" * 60)
        print(f"\n可能的原因:")
        print(f"  1. DATABASE_URL格式不正确")
        print(f"  2. 网络连接问题")
        print(f"  3. Neon数据库凭证错误")
        print(f"  4. 防火墙阻止连接")
else:
    print(f"\n❌ 错误: 未设置DATABASE_URL环境变量")
    print(f"\n请按以下步骤操作:")
    print(f"  1. 打开 .env 文件")
    print(f"  2. 将 DATABASE_URL 设置为您的Neon数据库连接字符串")
    print(f"  3. 格式: postgres://user:password@host/database?sslmode=require")
    print(f"  4. 保存文件后重新运行此脚本")

print("\n" + "=" * 60)
