#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复PostgreSQL目录创建错误
"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修改的行(2731-2737)
new_lines = []
i = 0
while i < len(lines):
    if i == 2730:  # 第2731行(索引2730)
        # 替换为新的代码
        new_lines.append('                # 确保数据目录存在(仅对SQLite)\n')
        new_lines.append('                db_uri = app.config[\'SQLALCHEMY_DATABASE_URI\']\n')
        new_lines.append('                if db_uri.startswith(\'sqlite:///\'):\n')
        new_lines.append('                    # SQLite需要创建本地目录\n')
        new_lines.append('                    db_path = db_uri.replace(\'sqlite:///\', \'\')\n')
        new_lines.append('                    db_dir = os.path.dirname(db_path)\n')
        new_lines.append('                    \n')
        new_lines.append('                    if db_dir and not os.path.exists(db_dir):\n')
        new_lines.append('                        os.makedirs(db_dir, exist_ok=True)\n')
        new_lines.append('                        print(f"Created database directory: {db_dir}")\n')
        new_lines.append('                # PostgreSQL不需要创建目录,跳过此步骤\n')
        i += 7  # 跳过原来的7行
    else:
        new_lines.append(lines[i])
        i += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('[OK] 修复成功!')
print('\n修改说明:')
print('- 添加了数据库类型判断,仅对SQLite创建目录')
print('- PostgreSQL跳过目录创建步骤')
print('- 避免了"postgresql:"路径错误')
print('\n现在可以重新启动应用,错误将不再出现!')
