#!/usr/bin/env python3
"""
数据库测试脚本
测试所有数据库模型是否可以正常访问
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ

def test_database_access():
    """测试数据库访问"""
    with app.app_context():
        print("=" * 60)
        print("数据库访问测试")
        print("=" * 60)
        print()

        # 测试每个模型
        models = [
            ('User', User),
            ('DigitalAsset', DigitalAsset),
            ('DigitalWill', DigitalWill),
            ('PlatformPolicy', PlatformPolicy),
            ('Story', Story),
            ('FAQ', FAQ)
        ]

        all_ok = True

        for model_name, model_class in models:
            try:
                count = model_class.query.count()
                print(f"[OK] {model_name:20s} - 记录数: {count}")
            except Exception as e:
                print(f"[FAIL] {model_name:20s} - 错误: {e}")
                all_ok = False

        print()
        print("=" * 60)

        if all_ok:
            print("[OK] 所有数据库模型访问正常")
        else:
            print("[FAIL] 部分数据库模型访问失败")

        print("=" * 60)

        # 测试详细数据
        print()
        print("=" * 60)
        print("数据库详细数据")
        print("=" * 60)
        print()

        # 平台政策
        print("平台政策:")
        policies = PlatformPolicy.query.all()
        for policy in policies:
            print(f"  - {policy.platform_name}: {policy.attitude}")
        print()

        # FAQ
        print("FAQ:")
        faqs = FAQ.query.all()
        for faq in faqs:
            print(f"  - [{faq.category}] {faq.question}")
        print()

        # 故事
        print("故事:")
        stories = Story.query.all()
        for story in stories:
            print(f"  - [{story.category}] {story.title}")
        print()

        return all_ok

if __name__ == '__main__':
    success = test_database_access()
    sys.exit(0 if success else 1)
