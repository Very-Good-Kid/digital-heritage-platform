"""
数据库路径诊断脚本
用于诊断数据库连接问题
"""
import os
import sys

print("=" * 60)
print("数据库路径诊断")
print("=" * 60)

# 获取当前工作目录
cwd = os.getcwd()
print(f"\n1. 当前工作目录: {cwd}")

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"2. 项目根目录: {project_root}")

# 检查instance目录
instance_dir = os.path.join(project_root, 'instance')
print(f"\n3. instance目录路径: {instance_dir}")
print(f"   - 存在: {os.path.exists(instance_dir)}")
print(f"   - 绝对路径: {os.path.abspath(instance_dir)}")

# 检查数据库文件
db_file = os.path.join(instance_dir, 'digital_heritage.db')
print(f"\n4. 数据库文件路径: {db_file}")
print(f"   - 存在: {os.path.exists(db_file)}")

if os.path.exists(db_file):
    file_size = os.path.getsize(db_file)
    print(f"   - 文件大小: {file_size} 字节")
else:
    print(f"   - 警告: 数据库文件不存在!")

# 测试配置加载
print(f"\n5. 测试配置加载...")
try:
    from config import config
    defaultConfig = config['default']
    print(f"   - 配置类: {defaultConfig.__name__}")
    print(f"   - DATA_DIR: {defaultConfig.DATA_DIR}")
    print(f"   - 数据库URI: {defaultConfig.SQLALCHEMY_DATABASE_URI}")
except Exception as e:
    print(f"   - 错误: {e}")
    import traceback
    traceback.print_exc()

# 测试SQLite连接
print(f"\n6. 测试SQLite连接...")
try:
    import sqlite3
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"   - 成功连接到数据库")
    print(f"   - 数据表数量: {len(tables)}")
    if tables:
        print(f"   - 数据表: {[t[0] for t in tables]}")
    conn.close()
except Exception as e:
    print(f"   - 错误: {e}")
    import traceback
    traceback.print_exc()

# 测试SQLAlchemy连接
print(f"\n7. 测试SQLAlchemy连接...")
try:
    from sqlalchemy import create_engine
    from models import db, User
    from app import app

    with app.app_context():
        # 测试查询
        user_count = User.query.count()
        print(f"   - 成功连接到数据库 (SQLAlchemy)")
        print(f"   - 用户数量: {user_count}")
except Exception as e:
    print(f"   - 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
