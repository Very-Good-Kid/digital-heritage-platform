# -*- coding: utf-8 -*-
"""
检查资产分类数据
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

print("=" * 60)
print("检查资产分类数据")
print("=" * 60)

# 检查本地SQLite
print("\n[1] 本地SQLite数据库:")
sqlite_engine = create_engine('sqlite:///instance/digital_heritage.db')
with sqlite_engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT category FROM digital_assets"))
    categories = [row[0] for row in result.fetchall()]
    print(f"   分类: {categories}")

    for cat in categories:
        result = conn.execute(text(f"SELECT COUNT(*) FROM digital_assets WHERE category = :cat"), {'cat': cat})
        count = result.fetchone()[0]
        print(f"   - {cat}: {count}个")

# 检查Neon数据库
database_url = os.environ.get('DATABASE_URL')
if database_url:
    print("\n[2] Neon PostgreSQL数据库:")
    neon_engine = create_engine(database_url)
    with neon_engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT category FROM digital_assets"))
        categories = [row[0] for row in result.fetchall()]
        print(f"   分类: {categories}")

        for cat in categories:
            result = conn.execute(text(f"SELECT COUNT(*) FROM digital_assets WHERE category = :cat"), {'cat': cat})
            count = result.fetchone()[0]
            print(f"   - {cat}: {count}个")

print("\n" + "=" * 60)
