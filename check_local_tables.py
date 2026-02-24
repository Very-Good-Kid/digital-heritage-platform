import sqlite3

conn = sqlite3.connect('instance/digital_heritage.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("本地SQLite数据库表:")
for table in tables:
    print(f"  - {table}")

conn.close()
