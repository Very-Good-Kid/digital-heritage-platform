"""
多租户配置模块
提供统一访问网址配置和租户识别功能
"""

class TenantConfig:
    """
    租户配置类
    管理多租户环境下的访问控制策略
    """

    # 多租户模式配置
    MULTI_TENANT_MODE = True  # 启用多租户模式

    # 统一访问配置
    UNIFIED_ACCESS_DOMAIN = None  # 统一访问域名（可选）

    # 数据隔离策略
    ISOLATION_STRATEGY = 'database'  # 'database' 或 'schema' 或 'row_level'

    # 管理员权限配置
    ADMIN_ACCESS_ALL = True  # 管理员可访问所有数据

    # 访问控制级别
    ACCESS_LEVEL = 'strict'  # 'strict' 严格模式, 'moderate' 中等模式

    @classmethod
    def get_tenant_config(cls):
        """
        获取当前租户配置
        :return: 配置字典
        """
        return {
            'multi_tenant': cls.MULTI_TENANT_MODE,
            'isolation_strategy': cls.ISOLATION_STRATEGY,
            'admin_access_all': cls.ADMIN_ACCESS_ALL,
            'access_level': cls.ACCESS_LEVEL
        }

    @classmethod
    def is_multi_tenant_enabled(cls):
        """是否启用多租户模式"""
        return cls.MULTI_TENANT_MODE


class AccessControlPolicy:
    """
    访问控制策略类
    定义不同用户角色的访问权限规则
    """

    # 权限级别
    PERMISSION_LEVELS = {
        'read': 1,      # 只读
        'write': 2,     # 读写
        'delete': 3,    # 删除
        'admin': 4       # 管理员权限
    }

    @classmethod
    def check_permission(cls, user, permission):
        """
        检查用户是否有指定权限
        :param user: 用户对象
        :param permission: 权限级别
        :return: (bool, str) - (是否有权限, 错误消息)
        """
        if not user or not user.is_authenticated:
            return False, '请先登录'

        # 管理员拥有所有权限
        if user.is_admin:
            return True, None

        # 普通用户权限检查
        if permission == cls.PERMISSION_LEVELS['read']:
            return True, None
        elif permission == cls.PERMISSION_LEVELS['write']:
            return True, None
        elif permission == cls.PERMISSION_LEVELS['delete']:
            return True, None
        elif permission == cls.PERMISSION_LEVELS['admin']:
            return False, '需要管理员权限'

        return False, '权限不足'

    @classmethod
    def can_access_all_data(cls, user):
        """用户是否可以访问所有数据"""
        return user.is_admin if user and user.is_authenticated else False

    @classmethod
    def get_user_filter(cls, user):
        """
        获取用户数据过滤条件
        管理员返回None（不过滤），普通用户返回user_id
        :param user: 用户对象
        :return: 过滤条件字典或None
        """
        if user and user.is_admin:
            return None
        return {'user_id': user.id} if user and user.is_authenticated else None


class ResourceOwnershipValidator:
    """
    资源所有权验证器
    确保用户只能访问自己拥有的资源
    """

    @staticmethod
    def validate(resource, user, require_admin=False):
        """
        验证资源所有权
        :param resource: 资源对象
        :param user: 当前用户
        :param require_admin: 是否需要管理员权限
        :return: (bool, str) - (是否可访问, 错误消息)
        """
        if not resource:
            return False, '资源不存在'

        if require_admin:
            if not user or not user.is_admin:
                return False, '此操作需要管理员权限'

        # 管理员可以访问所有资源
        if user and user.is_admin:
            return True, None

        # 检查资源所有权
        if hasattr(resource, 'user_id'):
            if resource.user_id != user.id:
                return False, '您没有权限访问此资源'

        return True, None

    @staticmethod
    def get_owner_id(resource):
        """
        获取资源所有者ID
        :param resource: 资源对象
        :return: 所有者ID或None
        """
        if hasattr(resource, 'user_id'):
            return resource.user_id
        return None


class DataIsolationPolicy:
    """
    数据隔离策略类
    定义不同级别的数据隔离规则
    """

    @staticmethod
    def apply_isolation(query, user, model_class):
        """
        应用数据隔离策略到查询
        :param query: SQLAlchemy查询对象
        :param user: 当前用户
        :param model_class: 模型类
        :return: 应用隔离后的查询
        """
        if not user or not user.is_authenticated:
            return query

        # 管理员不过滤数据
        if user.is_admin:
            return query

        # 确保模型有user_id字段
        if hasattr(model_class, 'user_id'):
            return query.filter_by(user_id=user.id)

        return query

    @staticmethod
    def get_accessible_resources(query, user, model_class):
        """
        获取用户可访问的资源
        :param query: SQLAlchemy查询对象
        :param user: 当前用户
        :param model_class: 模型类
        :return: 应用隔离后的查询结果
        """
        filtered_query = DataIsolationPolicy.apply_isolation(query, user, model_class)
        return filtered_query.all()

    @staticmethod
    def validate_cross_tenant_access(user, target_user_id):
        """
        验证跨租户访问
        :param user: 当前用户
        :param target_user_id: 目标用户ID
        :return: (bool, str) - (是否允许, 错误消息)
        """
        # 管理员可以访问所有用户数据
        if user.is_admin:
            return True, None

        # 用户不能访问其他用户的数据
        if target_user_id != user.id:
            return False, '您没有权限访问此用户的数据'

        return True, None
