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

    categories = ['社交媒体', '电子邮箱', '云存储与数字内容', '虚拟资产与数字货币', '其他数字资产']
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
        'customer_service': policy.customer_service,
        'legal_basis': policy.legal_basis,
        'risk_warning': policy.risk_warning
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


# ============================================================================
# 政策条款详情管理API
# ============================================================================

@admin_bp.route('/api/content/policies/<int:policy_id>/details', methods=['GET'])
@csrf_exempt
@admin_required
def api_policy_details(policy_id):
    """获取平台政策的条款详情列表"""
    from models import PlatformPolicy, PolicyDetail
    policy = PlatformPolicy.query.get(policy_id)
    if not policy:
        return jsonify({'success': False, 'message': '政策不存在'}), 404
    
    details = PolicyDetail.query.filter_by(platform_policy_id=policy_id).order_by(PolicyDetail.display_order).all()
    return jsonify({
        'platform_name': policy.platform_name,
        'details': [{
            'id': d.id,
            'policy_title': d.policy_title,
            'policy_text': d.policy_text,
            'legal_interpretation': d.legal_interpretation,
            'display_order': d.display_order
        } for d in details]
    })


@admin_bp.route('/api/content/policy-details/<int:detail_id>', methods=['GET'])
@csrf_exempt
@admin_required
def api_get_policy_detail(detail_id):
    """获取单个政策条款详情"""
    from models import PolicyDetail
    detail = PolicyDetail.query.get(detail_id)
    if not detail:
        return jsonify({'success': False, 'message': '条款不存在'}), 404
    
    return jsonify({
        'id': detail.id,
        'platform_policy_id': detail.platform_policy_id,
        'policy_title': detail.policy_title,
        'policy_text': detail.policy_text,
        'legal_interpretation': detail.legal_interpretation,
        'display_order': detail.display_order
    })


@admin_bp.route('/api/content/policy-details', methods=['POST'])
@csrf_exempt
@admin_required
def api_create_policy_detail():
    """创建政策条款详情"""
    from models import PolicyDetail
    data = request.json
    
    try:
        detail = PolicyDetail(
            platform_policy_id=data.get('platform_policy_id'),
            policy_title=data.get('policy_title'),
            policy_text=data.get('policy_text'),
            legal_interpretation=data.get('legal_interpretation'),
            display_order=data.get('display_order', 0)
        )
        db.session.add(detail)
        db.session.commit()
        return jsonify({'success': True, 'message': '政策条款创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@admin_bp.route('/api/content/policy-details/<int:detail_id>', methods=['PUT', 'PATCH'])
@csrf_exempt
@admin_required
def api_update_policy_detail(detail_id):
    """更新政策条款详情"""
    from models import PolicyDetail
    detail = PolicyDetail.query.get(detail_id)
    if not detail:
        return jsonify({'success': False, 'message': '条款不存在'}), 404
    
    data = request.json
    try:
        detail.policy_title = data.get('policy_title', detail.policy_title)
        detail.policy_text = data.get('policy_text', detail.policy_text)
        detail.legal_interpretation = data.get('legal_interpretation', detail.legal_interpretation)
        detail.display_order = data.get('display_order', detail.display_order)
        db.session.commit()
        return jsonify({'success': True, 'message': '政策条款更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@admin_bp.route('/api/content/policy-details/<int:detail_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_policy_detail(detail_id):
    """删除政策条款详情"""
    from models import PolicyDetail
    detail = PolicyDetail.query.get(detail_id)
    if not detail:
        return jsonify({'success': False, 'message': '条款不存在'}), 404
    
    try:
        db.session.delete(detail)
        db.session.commit()
        return jsonify({'success': True, 'message': '政策条款删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


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


@admin_bp.route('/sync')
@login_required
@admin_required
def sync():
    """数据同步页面"""
    return render_template('admin/sync.html')


# ============================================================================
# 数据同步端点
# ============================================================================

@admin_bp.route('/sync/faq', methods=['POST'])
@csrf_exempt
@admin_required
def sync_faq():
    """同步FAQ数据"""
    try:
        # FAQ数据（从本地导出）
        FAQ_DATA = [
            {"id": 1, "question": "数字资产包括哪些内容？", "answer": "数字资产是指公民合法拥有或控制的、以数字化形式存在、具有经济或社会价值的信息资源。按属性可分为：<br><strong>（1）财产型：</strong>虚拟货币（比特币等）、数字人民币、支付宝/微信余额、游戏装备/账号、NFT、数字版权、数据资产；<br><strong>（2）人格型：</strong>社交账号、邮件、聊天记录、相册、个人文档；<br><strong>（3）混合型：</strong>兼具财产与人格属性（如带粉丝/流量的自媒体账号）。<br><br>【依据】《信息技术服务 数据资产管理要求》："数据资产"是指合法拥有或控制的、能进行计量的、为组织带来经济和社会价值的数据资源。", "category": "概念与价值", "order": 1},
            {"id": 2, "question": "数字资产与传统资产有什么本质区别？", "answer": "<strong>（1）存在形式：</strong>无形、数字化、依赖平台/网络；传统遗产具有物理存在或明确的实物载体。<br><strong>（2）权属：</strong>部分仅享有使用权（如社交账号，所有权归平台）；传统遗产多为完整所有权。<br><strong>（3）继承规则：</strong>无专门细则，适用《民法典》原则+平台协议；传统遗产规则明确。<br><strong>（4）价值：</strong>兼具经济+人格价值；传统遗产多为单一经济价值。", "category": "概念与价值", "order": 2},
            {"id": 3, "question": "为什么需要规划数字资产？", "answer": "<strong>（1）法律层面：</strong>数字资产属合法财产，需依法继承（《民法典》第1122条）。<br><strong>（2）实操层面：</strong>避免账号冻结、资产灭失、隐私泄露、继承纠纷。<br><strong>（3）价值层面：</strong>保护经济价值（余额、虚拟财产）与情感价值（回忆、隐私）。<br><br>【依据】《民法典》第127条："数据、网络虚拟财产受法律保护"。<br>《民法典》第1122条："遗产是自然人死亡时遗留的个人合法财产。依照法律规定或者根据其性质不得继承的遗产，不得继承。"", "category": "概念与价值", "order": 3},
            {"id": 4, "question": "数字资产规划的最佳时间是什么时候？", "answer": "拥有重要数字资产时、重大人生节点（结婚、生子、立遗嘱）。", "category": "概念与价值", "order": 4},
            {"id": 5, "question": "什么是数字遗嘱？", "answer": "以数字化形式订立、载明数字资产分配与处置意愿的遗嘱，包括电子遗嘱、区块链遗嘱、云存储遗嘱等。核心是明确数字资产范围、继承人、访问方式与隐私处置规则。", "category": "概念与价值", "order": 5},
            {"id": 6, "question": "如何保护我的数字资产？", "answer": "<strong>(1)</strong>定期备份重要数据到本地或云端；<br><strong>(2)</strong>使用密码管理器安全存储密码；<br><strong>(3)</strong>创建数字遗嘱并定期更新；<br><strong>(4)</strong>告知家人重要账户信息；<br><strong>(5)</strong>了解各平台的继承政策；<br><strong>(6)</strong>启用双重认证；<br><strong>(7)</strong>定期检查账户安全设置。", "category": "安全与管理", "order": 1},
            {"id": 7, "question": "密码安全应该注意什么？", "answer": "<strong>(1)</strong>使用强密码（大小写字母、数字、特殊符号组合，至少12位）；<br><strong>(2)</strong>不要重复使用密码；<br><strong>(3)</strong>定期更换密码（每3-6个月）；<br><strong>(4)</strong>启用两步验证；<br><strong>(5)</strong>使用密码管理器（如LastPass、1Password）；<br><strong>(6)</strong>不要在公共场所输入密码；<br><strong>(7)</strong>警惕钓鱼网站。<br><br>【依据】《个人信息保护法》第51条："个人信息处理者应当根据个人信息的处理目的、处理方式、个人信息的种类以及对个人权益的影响、可能存在的安全风险等，采取相应的加密、去标识化等安全技术措施，确保个人信息处理活动符合法律规定，并防止未经授权的访问以及个人信息泄露、篡改、丢失。"", "category": "安全与管理", "order": 2},
        ]

        imported_count = 0
        updated_count = 0

        for faq_info in FAQ_DATA:
            # 检查是否已存在
            existing = FAQ.query.filter_by(id=faq_info['id']).first()

            if existing:
                # 更新现有记录
                existing.question = faq_info['question']
                existing.answer = faq_info['answer']
                existing.category = faq_info['category']
                existing.order = faq_info['order']
                updated_count += 1
            else:
                # 创建新记录
                faq = FAQ(
                    id=faq_info['id'],
                    question=faq_info['question'],
                    answer=faq_info['answer'],
                    category=faq_info['category'],
                    order=faq_info['order']
                )
                db.session.add(faq)
                imported_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'FAQ数据同步成功！新增 {imported_count} 条，更新 {updated_count} 条',
            'imported': imported_count,
            'updated': updated_count,
            'total': imported_count + updated_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'FAQ数据同步失败: {str(e)}'
        }), 500




