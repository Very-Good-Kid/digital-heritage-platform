#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员账户创建脚本

使用方法:
    python create_admin.py

交互式创建管理员账户
"""
import sys
import getpass
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, '.')

from app import app
from models import db, User


def create_admin():
    """创建管理员账户"""
    print("\n" + "="*50)
    print("          管理员账户创建工具")
    print("="*50 + "\n")

    with app.app_context():
        # 检查是否已有管理员
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"⚠️  警告: 系统中已存在管理员账户: {existing_admin.username}")
            print("   如果您想创建新的管理员账户，请继续\n")

        # 获取用户输入
        default_username = 'admin'
        username = input(f"请输入管理员用户名 [默认: {default_username}]: ").strip() or default_username

        default_email = 'admin@digitalheritage.com'
        email = input(f"请输入管理员邮箱 [默认: {default_email}]: ").strip() or default_email

        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            print(f"\n❌ 错误: 用户名 '{username}' 已存在")
            return False

        if User.query.filter_by(email=email).first():
            print(f"\n❌ 错误: 邮箱 '{email}' 已被注册")
            return False

        # 获取密码
        password = getpass.getpass("请输入管理员密码: ")
        if not password:
            print("\n❌ 错误: 密码不能为空")
            return False

        if len(password) < 6:
            print("\n❌ 错误: 密码长度不能少于6位")
            return False

        confirm_password = getpass.getpass("请再次输入密码确认: ")
        if password != confirm_password:
            print("\n❌ 错误: 两次输入的密码不一致")
            return False

        # 创建管理员
        admin = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=True,
            is_active=True
        )

        try:
            db.session.add(admin)
            db.session.commit()

            print("\n" + "="*50)
            print("✅ 管理员账户创建成功!")
            print("="*50)
            print(f"   用户名: {username}")
            print(f"   邮箱: {email}")
            print(f"   密码: {'*' * len(password)}")
            print(f"\n   请妥善保管管理员账户信息！")
            print(f"   访问地址: http://localhost:5000/admin")
            print("="*50 + "\n")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 错误: 创建管理员失败 - {str(e)}")
            return False


def list_admins():
    """列出所有管理员"""
    with app.app_context():
        admins = User.query.filter_by(is_admin=True).all()

        print("\n" + "="*50)
        print("          系统管理员列表")
        print("="*50 + "\n")

        if not admins:
            print("   系统中没有管理员账户\n")
        else:
            for idx, admin in enumerate(admins, 1):
                print(f"{idx}. {admin.username} ({admin.email})")
                print(f"   状态: {'启用' if admin.is_active else '禁用'}")
                print(f"   创建时间: {admin.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()

        print("="*50 + "\n")


def main():
    """主函数"""
    print("\n数字遗产管理平台 - 后台管理系统")
    print("--------------------------------")

    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == '--list' or command == '-l':
            list_admins()
            return

        if command == '--help' or command == '-h':
            print("""
用法:
    python create_admin.py              # 创建管理员账户 (交互式)
    python create_admin.py --list       # 列出所有管理员
    python create_admin.py -l           # 列出所有管理员
    python create_admin.py --help       # 显示帮助信息
    python create_admin.py -h           # 显示帮助信息
            """)
            return

    # 默认行为: 创建管理员
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {str(e)}")


if __name__ == '__main__':
    main()
