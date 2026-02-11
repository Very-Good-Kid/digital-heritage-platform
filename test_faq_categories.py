#!/usr/bin/env python3
"""测试 FAQ 分类和内容"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FAQ

with app.app_context():
    # 获取所有 FAQ
    faqs = FAQ.query.order_by(FAQ.category, FAQ.order).all()
    
    # 按指定顺序排序分类
    category_order = ['基础概念', '保护措施', '法律问题']
    categories = sorted(set(faq.category for faq in faqs), key=lambda x: category_order.index(x) if x in category_order else 999)
    
    print('Categories:', categories)
    print('\nFAQ by category:')
    for cat in categories:
        print(f'\n{cat}:')
        for faq in faqs:
            if faq.category == cat:
                print(f'  - {faq.question}')
