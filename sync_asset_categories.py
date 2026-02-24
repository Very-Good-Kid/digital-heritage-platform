# -*- coding: utf-8 -*-
"""
同步资产分类数据到Neon数据库
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

print("=" * 60)
print("同步资产分类数据到Neon")
print("=" * 60)

# 创建引擎
sqlite_engine = create_engine('sqlite:///instance/digital_heritage.db')
database_url = os.environ.get('DATABASE_URL')
neon_engine = create_engine(database_url)

# 分类映射(旧分类 -> 新分类)
category_mapping = {
    '虚拟财产': '虚拟资产与数字货币',
    '社交': '社交媒体',
    '金融': '电子邮箱',
    '记忆': '云存储与数字内容'
}

print("\n[1] 更新Neon数据库中的资产分类...")
with neon_engine.connect() as conn:
    updated_count = 0
    for old_cat, new_cat in category_mapping.items():
        # 检查是否有旧分类
        result = conn.execute(
            text("SELECT COUNT(*) FROM digital_assets WHERE category = :old_cat"),
            {'old_cat': old_cat}
        )
        count = result.fetchone()[0]

        if count > 0:
            print(f"   更新 '{old_cat}' -> '{new_cat}': {count}个资产")
            conn.execute(
                text("UPDATE digital_assets SET category = :new_cat WHERE category = :old_cat"),
                {'new_cat': new_cat, 'old_cat': old_cat}
            )
            updated_count += count

    conn.commit()
    print(f"   [OK] 共更新 {updated_count} 个资产分类")

print("\n[2] 验证更新结果...")
with neon_engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT category FROM digital_assets"))
    categories = [row[0] for row in result.fetchall()]
    print(f"   当前分类: {categories}")

    for cat in categories:
        result = conn.execute(
            text("SELECT COUNT(*) FROM digital_assets WHERE category = :cat"),
            {'cat': cat}
        )
        count = result.fetchone()[0]
        print(f"   - {cat}: {count}个")

print("\n" + "=" * 60)
print("[SUCCESS] 资产分类同步完成!")
print("=" * 60)
