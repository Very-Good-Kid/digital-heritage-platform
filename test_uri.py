"""
测试不同URI格式
"""
from sqlalchemy import create_engine
import os

db_path = os.path.abspath('instance/digital_heritage.db')
print(f"数据库路径: {db_path}")
print()

# 测试不同的URI格式
uris = [
    f"sqlite:///{db_path}",  # 3个斜杠（相对路径风格）
    f"sqlite:////{db_path}",  # 4个斜杠（绝对路径风格）
    f"sqlite:///{db_path.replace(os.sep, '/')}",  # 3个斜杠 + 正斜杠
    f"sqlite:////{db_path.replace(os.sep, '/')}",  # 4个斜杠 + 正斜杠
]

for uri in uris:
    print(f"测试URI: {uri}")
    try:
        engine = create_engine(uri)
        conn = engine.connect()
        print(f"  [OK] 成功连接")
        conn.close()
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
    print()
