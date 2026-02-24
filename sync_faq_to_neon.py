# -*- coding: utf-8 -*-
"""
将本地SQLite数据库的FAQ数据同步到Neon PostgreSQL数据库
"""
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, text

# 加载环境变量
load_dotenv()

print("=" * 60)
print("本地SQLite -> Neon PostgreSQL FAQ数据同步")
print("=" * 60)

# 检查DATABASE_URL
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("\n错误: 未设置DATABASE_URL环境变量")
    exit(1)

print("\n检测到Neon数据库配置")

try:
    # 创建SQLite引擎(本地)
    sqlite_engine = create_engine('sqlite:///instance/digital_heritage.db')

    # 创建PostgreSQL引擎(Neon)
    neon_engine = create_engine(database_url)

    print("\n" + "=" * 60)
    print("开始同步FAQ数据...")
    print("=" * 60)

    # 同步FAQ数据
    print("\n正在读取本地FAQ数据...")
    with sqlite_engine.connect() as sqlite_conn:
        result = sqlite_conn.execute(text("SELECT id, question, answer, category, \"order\" FROM faqs"))
        faqs = result.fetchall()
        print(f"   本地FAQ数量: {len(faqs)}")

    if not faqs:
        print("\n本地没有FAQ数据,无需同步")
        exit(0)

    print("\n正在同步到Neon数据库...")
    with neon_engine.connect() as neon_conn:
        imported_count = 0
        updated_count = 0

        for faq in faqs:
            faq_id, question, answer, category, order = faq
            # 检查是否已存在
            existing = neon_conn.execute(
                text("SELECT id FROM faqs WHERE id = :id"),
                {'id': faq_id}
            ).fetchone()

            if existing:
                # 更新
                neon_conn.execute(text("""
                    UPDATE faqs
                    SET question = :question, answer = :answer, category = :category, \"order\" = :order
                    WHERE id = :id
                """), {
                    'id': faq_id, 'question': question, 'answer': answer,
                    'category': category, 'order': order
                })
                updated_count += 1
            else:
                # 插入
                neon_conn.execute(text("""
                    INSERT INTO faqs (id, question, answer, category, \"order\")
                    VALUES (:id, :question, :answer, :category, :order)
                """), {
                    'id': faq_id, 'question': question, 'answer': answer,
                    'category': category, 'order': order
                })
                imported_count += 1

        neon_conn.commit()
        print(f"   [OK] FAQ数据同步完成")
        print(f"   - 新增: {imported_count} 条")
        print(f"   - 更新: {updated_count} 条")
        print(f"   - 总计: {imported_count + updated_count} 条")

    print("\n" + "=" * 60)
    print("[SUCCESS] FAQ数据同步完成!")
    print("=" * 60)
    print(f"\n同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    print(f"\n[ERROR] 同步失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
