"""
后台管理系统 - API响应格式和工具函数
"""
from flask import jsonify
from functools import wraps


class APIResponse:
    """API响应标准格式"""

    @staticmethod
    def success(data=None, message='操作成功'):
        """成功响应"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response)

    @staticmethod
    def error(message='操作失败', code=400):
        """错误响应"""
        return jsonify({
            'success': False,
            'message': message
        }), code

    @staticmethod
    def paginated(items, total, page, per_page):
        """分页响应"""
        return jsonify({
            'success': True,
            'data': items,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        })


def api_response(f):
    """API响应装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)

            # 如果返回的是tuple (response, status_code)
            if isinstance(result, tuple) and len(result) == 2:
                return result

            # 如果已经是响应对象
            if hasattr(result, 'json'):
                return result

            # 默认返回成功响应
            return APIResponse.success(result)

        except Exception as e:
            return APIResponse.error(str(e), 500)

    return decorated_function


def validate_required(data, required_fields):
    """验证必填字段"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f'缺少必填字段: {", ".join(missing_fields)}'
    return True, None
