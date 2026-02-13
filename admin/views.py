"""
后台管理系统 - 视图和API路由
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
# 自定义 csrf_exempt 装饰器
def csrf_exempt(view_func):
    """标记视图函数免除 CSRF 保护"""
    view_func.csrf_exempt = True
    return view_func
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ
from .decorators import admin_required
from .stats import get_dashboard_stats, get_user_growth_data, get_activity_data
from .crud import user_crud, asset_crud, will_crud, content_crud

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')


# ============================================================================
# 后台仪表盘
# ============================================================================

@admin_bp.route('/')
@login_required
def dashboard():
    """后台仪表盘首页"""
    if not current_user.is_admin:
        flash('需要管理员权限', 'error')
        return redirect(url_for('index'))

    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/api/stats')
@csrf_exempt
@admin_required
def api_stats():
    """获取统计数据API"""
    stats = get_dashboard_stats()
    return jsonify({'success': True, **stats})


@admin_bp.route('/api/charts/growth')
@csrf_exempt
@admin_required
def api_growth_chart():
    """获取用户增长图表数据"""
    days = request.args.get('days', 30, type=int)
    data = get_user_growth_data(days)
    return jsonify({'success': True, **data})


@admin_bp.route('/api/charts/activity')
@csrf_exempt
@admin_required
def api_activity_chart():
    """获取用户活动图表数据"""
    days = request.args.get('days', 7, type=int)
    data = get_activity_data(days)
    return jsonify({'success': True, **data})


# ============================================================================
# 用户管理
# ============================================================================

@admin_bp.route('/users')
@admin_required
def users():
    """用户管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')

    query = User.query

    # 搜索
    if search:
        query = query.filter(
            or_(
                User.username.like(f'%{search}%'),
                User.email.like(f'%{search}%')
            )
        )

    # 状态筛选
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'admin':
        query = query.filter_by(is_admin=True)

    # 分页
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/users.html', pagination=pagination, search=search, status=status)


@admin_bp.route('/api/users', methods=['GET'])
@csrf_exempt
@admin_required
def api_users():
    """获取用户列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')

    query = User.query

    if search:
        query = query.filter(
            or_(
                User.username.like(f'%{search}%'),
                User.email.like(f'%{search}%')
            )
        )

    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'admin':
        query = query.filter_by(is_admin=True)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
        'assets_count': user.digital_assets.count(),
        'wills_count': user.digital_wills.count()
    } for user in pagination.items]

    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/api/users/<int:user_id>', methods=['GET'])
@csrf_exempt
@admin_required
def api_user_detail(user_id):
    """获取用户详情API"""
    user = User.query.get_or_404(user_id)

    try:
        assets = user.digital_assets.limit(10).all()
        wills = user.digital_wills.limit(10).all()
    except Exception as e:
        assets = []
        wills = []

    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
        'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else '',
        'assets_count': user.digital_assets.count(),
        'wills_count': user.digital_wills.count(),
        'assets': [{
            'id': asset.id,
            'platform_name': asset.platform_name,
            'account': asset.account,
            'category': asset.category,
            'created_at': asset.created_at.strftime('%Y-%m-%d') if asset.created_at else ''
        } for asset in assets],
        'wills': [{
            'id': will.id,
            'title': will.title,
            'status': will.status,
            'created_at': will.created_at.strftime('%Y-%m-%d') if will.created_at else ''
        } for will in wills]
    }

    return jsonify({
        'success': True,
        'data': data
    })


@admin_bp.route('/api/users', methods=['POST'])
@csrf_exempt
@admin_required
def api_create_user():
    """创建用户API"""
    return user_crud.create_user(request.json)


@admin_bp.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
@csrf_exempt
@admin_required
def api_update_user(user_id):
    """更新用户API"""
    return user_crud.update_user(user_id, request.json)


@admin_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@csrf_exempt
@admin_required
def api_toggle_user_status(user_id):
    """切换用户状态API"""
    return user_crud.toggle_status(user_id)


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_user(user_id):
    """删除用户API"""
    return user_crud.delete_user(user_id)


# ============================================================================
# 数字资产管理
# ============================================================================

@admin_bp.route('/assets')
@admin_required
def assets():
    """数字资产管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', 'all')

    query = DigitalAsset.query

    # 搜索
    if search:
        query = query.filter(
            or_(
                DigitalAsset.platform_name.like(f'%{search}%'),
                DigitalAsset.account.like(f'%{search}%')
            )
        )

    # 分类筛选
    if category != 'all':
        query = query.filter_by(category=category)

    # 分页
    pagination = query.order_by(DigitalAsset.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = ['社交', '金融', '记忆', '虚拟财产']
    return render_template('admin/assets.html', pagination=pagination, search=search, category=category, categories=categories)


@admin_bp.route('/api/assets', methods=['GET'])
@csrf_exempt
@admin_required
def api_assets():
    """获取数字资产列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', 'all')

    query = DigitalAsset.query

    # 应用数据隔离策略：管理员看所有，普通用户只看自己的
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(
            or_(
                DigitalAsset.platform_name.like(f'%{search}%'),
                DigitalAsset.account.like(f'%{search}%')
            )
        )

    if category != 'all':
        query = query.filter_by(category=category)

    pagination = query.order_by(DigitalAsset.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    assets = [{
        'id': asset.id,
        'user_id': asset.user_id,
        'username': asset.user.username if asset.user else 'Unknown',
        'platform_name': asset.platform_name,
        'account': asset.account,
        'category': asset.category,
        'notes': asset.notes,
        'created_at': asset.created_at.strftime('%Y-%m-%d')
    } for asset in pagination.items]

    return jsonify({
        'assets': assets,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/api/assets/<int:asset_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_asset(asset_id):
    """删除数字资产API"""
    return asset_crud.delete_asset(asset_id)


# ============================================================================
# 数字遗嘱管理
# ============================================================================

@admin_bp.route('/wills')
@admin_required
def wills():
    """数字遗嘱管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')

    query = DigitalWill.query

    # 搜索
    if search:
        query = query.filter(
            or_(
                DigitalWill.title.like(f'%{search}%'),
                DigitalWill.description.like(f'%{search}%')
            )
        )

    # 状态筛选
    if status != 'all':
        query = query.filter_by(status=status)

    # 分页
    pagination = query.order_by(DigitalWill.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/wills.html', pagination=pagination, search=search, status=status)


@admin_bp.route('/api/wills', methods=['GET'])
@csrf_exempt
@admin_required
def api_wills():
    """获取数字遗嘱列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')

    query = DigitalWill.query

    # 应用数据隔离策略：管理员看所有，普通用户只看自己的
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(
            or_(
                DigitalWill.title.like(f'%{search}%'),
                DigitalWill.description.like(f'%{search}%')
            )
        )

    if status != 'all':
        query = query.filter_by(status=status)

    pagination = query.order_by(DigitalWill.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    wills = [{
        'id': will.id,
        'user_id': will.user_id,
        'username': will.user.username if will.user else 'Unknown',
        'title': will.title,
        'description': will.description[:100] if will.description else '',
        'status': will.status,
        'created_at': will.created_at.strftime('%Y-%m-%d')
    } for will in pagination.items]

    return jsonify({
        'wills': wills,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/api/wills/<int:will_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_will(will_id):
    """删除数字遗嘱API"""
    return will_crud.delete_will(will_id)


@admin_bp.route('/api/wills/<int:will_id>/status', methods=['PUT'])
@csrf_exempt
@admin_required
def api_update_will_status(will_id):
    """更新遗嘱状态API"""
    return will_crud.update_will_status(will_id, request.json)

# ============================================================================
# 内容管理
# ============================================================================

@admin_bp.route('/content/policies')
@admin_required
def policies():
    """平台政策管理页面"""
    policies = PlatformPolicy.query.order_by(PlatformPolicy.platform_name).all()
    return render_template('admin/policies.html', policies=policies)


@admin_bp.route('/api/content/policies', methods=['GET'])
@csrf_exempt
@admin_required
def api_policies():
    """获取平台政策列表API"""
    policies = PlatformPolicy.query.order_by(PlatformPolicy.platform_name).all()
    data = [{
        'id': policy.id,
        'platform_name': policy.platform_name,
        'policy_content': policy.policy_content,
        'attitude': policy.attitude,
        'inherit_possibility': policy.inherit_possibility,
        'customer_service': policy.customer_service
    } for policy in policies]
    return jsonify(data)


@admin_bp.route('/api/content/policies', methods=['POST'])
@csrf_exempt
@admin_required
def api_create_policy():
    """创建平台政策API"""
    return content_crud.create_policy(request.json)


@admin_bp.route('/api/content/policies/<int:policy_id>', methods=['PUT', 'PATCH'])
@csrf_exempt
@admin_required
def api_update_policy(policy_id):
    """更新平台政策API"""
    return content_crud.update_policy(policy_id, request.json)


@admin_bp.route('/api/content/policies/<int:policy_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_policy(policy_id):
    """删除平台政策API"""
    return content_crud.delete_policy(policy_id)


@admin_bp.route('/content/faqs')
@admin_required
def faqs():
    """FAQ管理页面"""
    faqs = FAQ.query.order_by(FAQ.category, FAQ.order).all()
    return render_template('admin/faqs.html', faqs=faqs)


@admin_bp.route('/api/content/faqs', methods=['GET'])
@csrf_exempt
@admin_required
def api_faqs():
    """获取FAQ列表API"""
    faqs = FAQ.query.order_by(FAQ.category, FAQ.order).all()
    data = [{
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'category': faq.category,
        'order': faq.order
    } for faq in faqs]
    return jsonify(data)


@admin_bp.route('/api/content/faqs', methods=['POST'])
@csrf_exempt
@admin_required
def api_create_faq():
    """创建FAQ API"""
    return content_crud.create_faq(request.json)


@admin_bp.route('/api/content/faqs/<int:faq_id>', methods=['PUT', 'PATCH'])
@csrf_exempt
@admin_required
def api_update_faq(faq_id):
    """更新FAQ API"""
    return content_crud.update_faq(faq_id, request.json)


@admin_bp.route('/api/content/faqs/<int:faq_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_faq(faq_id):
    """删除FAQ API"""
    return content_crud.delete_faq(faq_id)


@admin_bp.route('/content/stories')
@admin_required
def stories():
    """故事管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', 'all')

    query = Story.query

    if status != 'all':
        query = query.filter_by(status=status)

    pagination = query.order_by(Story.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/stories.html', pagination=pagination, status=status)


@admin_bp.route('/api/content/stories', methods=['GET'])
@csrf_exempt
@admin_required
def api_stories():
    """获取故事列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', 'all')

    query = Story.query

    if status != 'all':
        query = query.filter_by(status=status)

    pagination = query.order_by(Story.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    stories = [{
        'id': story.id,
        'title': story.title,
        'content': story.content[:100],
        'author': story.author,
        'category': story.category,
        'status': story.status,
        'created_at': story.created_at.strftime('%Y-%m-%d')
    } for story in pagination.items]

    return jsonify({
        'stories': stories,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/api/content/stories/<int:story_id>/approve', methods=['POST'])
@csrf_exempt
@admin_required
def api_approve_story(story_id):
    """审核通过故事API"""
    return content_crud.approve_story(story_id)


@admin_bp.route('/api/content/stories/<int:story_id>/reject', methods=['POST'])
@csrf_exempt
@admin_required
def api_reject_story(story_id):
    """审核拒绝故事API"""
    return content_crud.reject_story(story_id)


@admin_bp.route('/api/content/stories/<int:story_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_story(story_id):
    """删除故事API"""
    return content_crud.delete_story(story_id)


# ============================================================================
# 系统设置
# ============================================================================

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """系统设置页面"""
    if not current_user.is_admin:
        flash('需要管理员权限', 'error')
        return redirect(url_for('index'))

    return render_template('admin/settings.html')


