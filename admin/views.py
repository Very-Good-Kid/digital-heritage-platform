"""
后台管理系统 - 视图和API路由
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

# 自定义 csrf_exempt 装饰器
def csrf_exempt(view_func):
    """豁免CSRF保护的装饰器"""
    view_func.csrf_exempt = True
    return view_func

from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ, ExternalKnowledge, ExternalKnowledgeChunk
from .decorators import admin_required
from .stats import get_dashboard_stats, get_user_growth_data, get_activity_data
from .crud import user_crud, asset_crud, will_crud, content_crud

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


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

    # 从数据库动态获取分类列表
    from sqlalchemy import distinct
    categories = [c[0] for c in db.session.query(distinct(DigitalAsset.category)).order_by(DigitalAsset.category).all()]

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
# 数字资产处置意愿声明书管理
# ============================================================================

@admin_bp.route('/wills')
@admin_required
def wills():
    """数字资产处置意愿声明书管理页面"""
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
    """获取数字资产处置意愿声明书列表API"""
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
    """删除数字资产处置意愿声明书API"""
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
# AI 知识库管理
# ============================================================================

@admin_bp.route('/knowledge')
@login_required
@admin_required
def knowledge():
    """AI知识库管理页面 - 管理员上传/查看/删除知识库文件"""
    return render_template('admin/knowledge.html')


# ============================================================================
# 数据同步端点
# ============================================================================

@admin_bp.route('/sync/faq', methods=['POST'])
@csrf_exempt
@admin_required
def sync_faq():
    """同步FAQ数据"""
    import json
    import os
    import sys

    try:
        # 打印调试信息
        print(f"[FAQ同步] 开始同步FAQ数据")
        print(f"[FAQ同步] 当前目录: {os.getcwd()}")

        # 从JSON文件读取FAQ数据
        faq_json_path = os.path.join(os.path.dirname(__file__), '..', 'faq_export_20260224_195547.json')
        print(f"[FAQ同步] 尝试读取: {faq_json_path}")

        if not os.path.exists(faq_json_path):
            # 如果找不到特定文件，尝试找最新的导出文件
            import glob
            search_dir = os.path.join(os.path.dirname(__file__), '..')
            faq_files = glob.glob(os.path.join(search_dir, 'faq_export_*.json'))
            print(f"[FAQ同步] 搜索目录: {search_dir}")
            print(f"[FAQ同步] 找到文件: {faq_files}")

            if faq_files:
                faq_json_path = max(faq_files, key=os.path.getctime)
                print(f"[FAQ同步] 使用文件: {faq_json_path}")
            else:
                return jsonify({
                    'success': False,
                    'message': '未找到FAQ导出文件，请先运行 sync_faq.py 导出数据'
                }), 400

        with open(faq_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        FAQ_DATA = data.get('faqs', [])
        print(f"[FAQ同步] 读取到 {len(FAQ_DATA)} 条FAQ数据")

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


# ============================================================================
# AI对话次数管理
# ============================================================================

@admin_bp.route('/api/users/<int:user_id>/chat-limit', methods=['POST'])
@csrf_exempt
@admin_required
def api_set_chat_limit(user_id):
    """设置用户的每日AI对话次数限制

    请求体(JSON):
        - daily_chat_limit: 每日次数上限(int)，0表示禁止，-1表示不限
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    limit = data.get('daily_chat_limit')

    if limit is None or not isinstance(limit, int) or limit < -1:
        return jsonify({'success': False, 'message': '无效的次数限制值'}), 400

    user.daily_chat_limit = limit
    try:
        db.session.commit()
        return jsonify({'success': True, 'daily_chat_limit': limit})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/chat-usage')
@csrf_exempt
@admin_required
def api_chat_usage():
    """获取所有用户的今日对话使用情况

    返回(JSON):
        - usage: [{user_id, username, daily_chat_limit, used_today, remaining}, ...]
    """
    from models import ChatUsage
    from models import get_china_time
    today = get_china_time().strftime('%Y-%m-%d')

    users = User.query.filter_by(is_admin=False).order_by(User.id).all()
    usage_map = {}
    usages = ChatUsage.query.filter_by(usage_date=today).all()
    for u in usages:
        usage_map[u.user_id] = u.count

    result = []
    for user in users:
        used = usage_map.get(user.id, 0)
        limit = user.daily_chat_limit if user.daily_chat_limit is not None else 5
        remaining = 999 if limit == -1 else max(0, limit - used)
        result.append({
            'user_id': user.id,
            'username': user.username,
            'daily_chat_limit': limit,
            'used_today': used,
            'remaining': remaining
        })

    return jsonify({'usage': result, 'date': today})


# ============================================================================
# 外部知识库管理（支持多提供者：网页/飞书Wiki/通用API）
# ============================================================================

@admin_bp.route('/api/external-knowledge/providers', methods=['GET'])
@csrf_exempt
@admin_required
def api_external_knowledge_providers():
    """获取所有可用的知识库提供者信息及表单字段定义"""
    from ai.knowledge_providers import get_all_providers_info
    return jsonify({'success': True, 'providers': get_all_providers_info()})


@admin_bp.route('/api/external-knowledge', methods=['GET'])
@csrf_exempt
@admin_required
def api_list_external_knowledge():
    """获取外部知识库链接列表"""
    links = ExternalKnowledge.query.order_by(ExternalKnowledge.created_at.desc()).all()
    # 提供者显示名称映射
    from ai.knowledge_providers import PROVIDER_REGISTRY
    data = [{
        'id': link.id,
        'name': link.name,
        'url': link.url,
        'provider': link.provider,
        'provider_display': PROVIDER_REGISTRY.get(link.provider, type('obj', (object,), {'display_name': link.provider})).display_name if PROVIDER_REGISTRY.get(link.provider) else link.provider,
        'is_active': link.is_active,
        'last_synced': link.last_synced.strftime('%Y-%m-%d %H:%M') if link.last_synced else '从未同步',
        'chunk_count': link.chunk_count,
        'created_at': link.created_at.strftime('%Y-%m-%d %H:%M') if link.created_at else ''
    } for link in links]
    return jsonify({'success': True, 'links': data})


def _sync_knowledge_from_provider(link):
    """
    核心同步函数：通过对应提供者获取内容 → 切分 → 向量化 → 存储
    
    Args:
        link: ExternalKnowledge 实例
    
    Returns:
        tuple: (success: bool, message: str, chunk_count: int)
    """
    from ai.knowledge_providers import get_provider
    from ai.chunker import split_text
    from ai.embedding import embed_texts
    import json
    from models import get_china_time

    # 获取提供者实例并验证配置
    config = link.get_config()
    try:
        provider = get_provider(link.provider, config)
    except ValueError as e:
        return False, str(e), 0

    valid, msg = provider.validate_config()
    if not valid:
        return False, f"配置不完整: {msg}", 0

    # 通过提供者获取内容
    try:
        text = provider.fetch_content()
    except Exception as e:
        return False, f"获取内容失败: {str(e)}", 0

    # 切分文本
    chunks = split_text(text, chunk_size=500, chunk_overlap=50)
    if not chunks:
        return False, "内容切分后无有效片段", 0

    # 生成向量
    try:
        embeddings = embed_texts(chunks)
    except Exception as emb_err:
        return False, f"向量化失败: {str(emb_err)}", 0

    # 删除旧chunks，写入新chunks
    ExternalKnowledgeChunk.query.filter_by(external_id=link.id).delete()
    for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        chunk = ExternalKnowledgeChunk(
            external_id=link.id,
            chunk_index=idx,
            content=chunk_text,
            embedding=json.dumps(embedding, ensure_ascii=False)
        )
        db.session.add(chunk)

    link.chunk_count = len(chunks)
    link.last_synced = get_china_time()

    return True, f"成功同步，共 {len(chunks)} 个知识片段", len(chunks)


@admin_bp.route('/api/external-knowledge', methods=['POST'])
@csrf_exempt
@admin_required
def api_add_external_knowledge():
    """添加外部知识库链接并通过对应提供者API同步内容"""
    data = request.json
    name = data.get('name', '').strip()
    provider_type = data.get('provider', 'webpage')
    config = {k: v for k, v in data.items() if k not in ('name', 'provider')}

    if not name:
        return jsonify({'success': False, 'message': '名称不能为空'}), 400

    # 验证提供者类型是否合法
    from ai.knowledge_providers import PROVIDER_REGISTRY
    if provider_type not in PROVIDER_REGISTRY:
        available = ', '.join(PROVIDER_REGISTRY.keys())
        return jsonify({'success': False, 'message': f'不支持的提供者类型: {provider_type}，可选: {available}'}), 400

    # 创建记录
    ext = ExternalKnowledge(
        user_id=current_user.id,
        name=name,
        provider=provider_type,
        is_active=True
    )
    ext.set_config(config)
    db.session.add(ext)
    db.session.flush()

    # 执行同步
    success, message, chunk_count = _sync_knowledge_from_provider(ext)

    if success:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'"{name}" - {message}',
            'chunk_count': chunk_count
        })
    else:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {message}'}), 400


@admin_bp.route('/api/external-knowledge/<int:link_id>', methods=['DELETE'])
@csrf_exempt
@admin_required
def api_delete_external_knowledge(link_id):
    """删除外部知识库链接及其所有片段"""
    link = ExternalKnowledge.query.get_or_404(link_id)
    try:
        db.session.delete(link)
        db.session.commit()
        return jsonify({'success': True, 'message': '已删除外部知识库链接'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@admin_bp.route('/api/external-knowledge/<int:link_id>/toggle', methods=['POST'])
@csrf_exempt
@admin_required
def api_toggle_external_knowledge(link_id):
    """启用/禁用外部知识库链接"""
    link = ExternalKnowledge.query.get_or_404(link_id)
    link.is_active = not link.is_active
    try:
        db.session.commit()
        return jsonify({'success': True, 'is_active': link.is_active})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/api/external-knowledge/<int:link_id>/sync', methods=['POST'])
@csrf_exempt
@admin_required
def api_sync_external_knowledge(link_id):
    """重新同步外部知识库链接内容"""
    link = ExternalKnowledge.query.get_or_404(link_id)

    try:
        success, message, chunk_count = _sync_knowledge_from_provider(link)
        if success:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'"{link.name}" - {message}',
                'chunk_count': chunk_count
            })
        else:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'同步失败: {message}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'同步异常: {str(e)}'}), 500


