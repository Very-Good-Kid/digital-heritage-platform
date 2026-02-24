# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url)

with engine.connect() as conn:
    # 检查user表结构
    print("User表结构:")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position;
    """))
    for row in result.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\nFAQ表结构:")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'faqs'
        ORDER BY ordinal_position;
    """))
    for row in result.fetchall():
        print(f"  {row[0]}: {row[1]}")
