"""
后台管理 - 多租户访问控制中间件
"""
from functools import wraps
from flask import jsonify, request, g
from flask_login import current_user
from models import DigitalAsset, DigitalWill, User, Story


def require_ownership(view_func):
    """
    装饰器：确保用户只能访问自己的资源，管理员可访问所有
    用于数字资产、数字遗嘱等用户资源
    """
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        # 管理员可以访问所有资源
        if current_user.is_admin:
            return view_func(*args, **kwargs)

        # 非管理员用户只能访问自己的资源
        resource_id = kwargs.get('id') or kwargs.get('will_id') or kwargs.get('asset_id')

        if resource_id:
            # 检查资源所有权
            if DigitalAsset.__name__ in str(view_func) or 'asset' in str(view_func):
                resource = DigitalAsset.query.get(resource_id)
                if resource and resource.user_id != current_user.id:
                    return jsonify({
                        'success': False,
                        'message': '您没有权限访问此资源'
                    }), 403

            elif DigitalWill.__name__ in str(view_func) or 'will' in str(view_func):
                resource = DigitalWill.query.get(resource_id)
                if resource and resource.user_id != current_user.id:
                    return jsonify({
                        'success': False,
                        'message': '您没有权限访问此资源'
                    }), 403

        return view_func(*args, **kwargs)

    return decorated_function


def require_admin_or_ownership(view_func):
    """
    装饰器：管理员可访问所有资源，用户只能访问自己的资源
    用于资源列表API，确保返回的数据范围正确
    """
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        # 将用户ID存入g对象，供后续查询使用
        if current_user.is_admin:
            g.filter_user_id = None  # 管理员不过滤用户
        else:
            g.filter_user_id = current_user.id  # 普通用户只看自己的数据

        return view_func(*args, **kwargs)

    return decorated_function


def tenant_isolation_query(query, model_class):
    """
    辅助函数：为查询添加多租户过滤条件
    管理员返回原查询，普通用户添加user_id过滤
    """
    if not current_user.is_admin:
        # 确保模型有user_id字段
        if hasattr(model_class, 'user_id'):
            query = query.filter_by(user_id=current_user.id)

    return query


def validate_resource_ownership(resource, user_id, require_admin=False):
    """
    验证资源所有权
    :param resource: 资源对象
    :param user_id: 用户ID
    :param require_admin: 是否需要管理员权限
    :return: (bool, str) - (是否有权限, 错误消息)
    """
    if require_admin and not user_id or not user_id.is_admin:
        return False, '此操作需要管理员权限'

    # 检查资源是否属于当前用户
    if hasattr(resource, 'user_id'):
        if resource.user_id != user_id:
            return False, '您没有权限访问此资源'

    return True, None


def get_accessible_data(query, model_class, current_user):
    """
    获取用户可访问的数据
    管理员可以访问所有数据，普通用户只能访问自己的数据
    """
    if current_user.is_admin:
        return query
    else:
        # 确保模型有user_id字段
        if hasattr(model_class, 'user_id'):
            return query.filter_by(user_id=current_user.id)
        return query


class TenantContext:
    """
    租户上下文管理类
    用于管理多租户环境下的数据访问范围
    """

    def __init__(self, user):
        self.user = user
        self.is_admin = user.is_admin if user else False
        self.user_id = user.id if user else None

    def can_access_all_data(self):
        """是否可以访问所有数据"""
        return self.is_admin

    def get_user_filter(self):
        """获取用户过滤条件"""
        if self.is_admin:
            return None
        return {'user_id': self.user_id}

    def validate_access(self, resource):
        """
        验证是否可以访问资源
        :param resource: 要访问的资源对象
        :return: (bool, str) - (是否可访问, 错误消息)
        """
        if not resource:
            return False, '资源不存在'

        # 管理员可以访问所有资源
        if self.is_admin:
            return True, None

        # 检查资源所有权
        if hasattr(resource, 'user_id'):
            if resource.user_id != self.user_id:
                return False, '您没有权限访问此资源'

        return True, None
