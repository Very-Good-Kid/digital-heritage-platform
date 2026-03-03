#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复PostgreSQL目录创建错误
"""

import re

# 读取文件
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换
old_code = '''                with app.app_context():
                    # 确保数据目录存在
                    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                    db_dir = os.path.dirname(db_path)

                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir, exist_ok=True)
                        print(f"Created database directory: {db_dir}")'''

new_code = '''                with app.app_context():
                    # 确保数据目录存在(仅对SQLite)
                    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
                    if db_uri.startswith('sqlite:///'):
                        # SQLite需要创建本地目录
                        db_path = db_uri.replace('sqlite:///', '')
                        db_dir = os.path.dirname(db_path)
                        
                        if db_dir and not os.path.exists(db_dir):
                            os.makedirs(db_dir, exist_ok=True)
                            print(f"Created database directory: {db_dir}")
                    # PostgreSQL不需要创建目录,跳过此步骤'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] 修复成功!')
    print('\n修改说明:')
    print('- 添加了数据库类型判断,仅对SQLite创建目录')
    print('- PostgreSQL跳过目录创建步骤')
    print('- 避免了"postgresql:"路径错误')
else:
    print('[FAILED] 未找到匹配的代码,可能已经修复或代码格式不同')
    print('\n尝试查找相关代码...')
    
    # 查找包含"确保数据目录存在"的行
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '确保数据目录存在' in line:
            print(f'找到相关代码在第{i+1}行:')
            print(f'  {line}')
            # 显示前后几行
            start = max(0, i-2)
            end = min(len(lines), i+8)
            print('\n上下文:')
            for j in range(start, end):
                marker = '>>>' if j == i else '   '
                print(f'{marker} {j+1}: {lines[j]}')
