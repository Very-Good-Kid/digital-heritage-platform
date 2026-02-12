"""
数据库文件检查脚本
"""
import os
import sys

print("=" * 60)
print("数据库文件检查")
print("=" * 60)

# 检查数据库文件
db_file = os.path.abspath('instance/digital_heritage.db')
print(f"\n1. 数据库文件路径: {db_file}")
print(f"   - 存在: {os.path.exists(db_file)}")

if os.path.exists(db_file):
    file_size = os.path.getsize(db_file)
    print(f"   - 文件大小: {file_size} 字节")

    # 检查文件权限
    if os.access(db_file, os.R_OK):
        print(f"   - 可读: 是")
    else:
        print(f"   - 可读: 否")

    if os.access(db_file, os.W_OK):
        print(f"   - 可写: 是")
    else:
        print(f"   - 可写: 否")

    # 检查是否有锁文件
    lock_file = db_file + '-journal'
    if os.path.exists(lock_file):
        print(f"   - 警告: 发现锁文件 {lock_file}")
        print(f"   - 这可能意味着另一个进程正在访问数据库")

    lock_file2 = db_file + '-wal'
    if os.path.exists(lock_file2):
        print(f"   - 警告: 发现WAL文件 {lock_file2}")
        print(f"   - 这可能意味着另一个进程正在访问数据库")
else:
    print(f"   - 错误: 数据库文件不存在!")

# 检查目录权限
instance_dir = os.path.dirname(db_file)
print(f"\n2. instance目录: {instance_dir}")
print(f"   - 存在: {os.path.exists(instance_dir)}")

if os.path.exists(instance_dir):
    if os.access(instance_dir, os.W_OK):
        print(f"   - 可写: 是")
    else:
        print(f"   - 可写: 否 - 这可能是问题所在!")

# 尝试直接打开数据库
print(f"\n3. 尝试直接打开数据库...")
try:
    import sqlite3
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
    table_count = cursor.fetchone()[0]
    print(f"   - 成功! 数据表数量: {table_count}")
    conn.close()
except Exception as e:
    print(f"   - 失败: {e}")

# 尝试使用SQLAlchemy
print(f"\n4. 尝试使用SQLAlchemy...")
try:
    from config import config
    defaultConfig = config['default']
    print(f"   - 数据库URI: {defaultConfig.SQLALCHEMY_DATABASE_URI}")

    from sqlalchemy import create_engine
    engine = create_engine(defaultConfig.SQLALCHEMY_DATABASE_URI)
    conn = engine.connect()
    print(f"   - 成功! SQLAlchemy连接正常")
    conn.close()
except Exception as e:
    print(f"   - 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
