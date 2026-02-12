"""
后台管理系统 - 认证和权限工具
"""
from flask_login import current_user
from functools import wraps
from flask import abort


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def is_admin():
    """检查当前用户是否为管理员"""
    return current_user.is_authenticated and current_user.is_admin


def can_edit_user(user_id):
    """检查是否可以编辑指定用户"""
    if not current_user.is_authenticated:
        return False

    # 管理员可以编辑所有用户
    if current_user.is_admin:
        return True

    # 用户只能编辑自己
    return current_user.id == user_id


def can_delete_user(user_id):
    """检查是否可以删除指定用户"""
    if not current_user.is_authenticated or not current_user.is_admin:
        return False

    # 管理员不能删除自己
    return current_user.id != user_id


def can_view_user_data(user_id):
    """检查是否可以查看用户数据"""
    if not current_user.is_authenticated:
        return False

    # 管理员可以查看所有用户数据
    if current_user.is_admin:
        return True

    # 用户只能查看自己的数据
    return current_user.id == user_id
