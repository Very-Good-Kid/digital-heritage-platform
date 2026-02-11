#!/usr/bin/env python3
"""检查 FAQ 数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FAQ

with app.app_context():
    count = FAQ.query.count()
    print(f'FAQ count: {count}')
    
    if count == 0:
        print('没有 FAQ 数据！')
    else:
        print('\nFAQ 列表:')
        faqs = FAQ.query.order_by(FAQ.category, FAQ.order).all()
        for faq in faqs:
            print(f'  [{faq.category}] {faq.question}')
