# 后台管理系统包初始化
from .views import admin_bp
from .auth import admin_required
from .decorators import role_required

__all__ = ['admin_bp', 'admin_required', 'role_required']
