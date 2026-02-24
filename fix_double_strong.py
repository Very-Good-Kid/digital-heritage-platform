# -*- coding: utf-8 -*-
"""
修复重复的<strong>标签
"""
import re

# 读取文件
with open('templates/inheritance/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除重复的<strong>标签
content = re.sub(r'<strong><strong>', '<strong>', content)
content = re.sub(r'</strong></strong>', '</strong>', content)

# 写回文件
with open('templates/inheritance/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] 重复标签已修复!")
