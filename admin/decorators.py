"""
后台管理系统 - 权限装饰器
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))

        if not current_user.is_admin:
            flash('需要管理员权限', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """基于角色的权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('login'))

            if not current_user.is_admin:
                flash('需要管理员权限', 'error')
                return redirect(url_for('index'))

            # 扩展：未来可以添加更多角色
            # if current_user.role not in roles:
            #     flash('权限不足', 'error')
            #     return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
