"""
后台管理系统 - 数据统计模块 - 性能优化版
"""
from datetime import datetime, timedelta
from sqlalchemy import func
import time

from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ, get_china_time


# 简单的内存缓存
_stats_cache = {'data': None, 'timestamp': 0}
_CACHE_TTL = 30  # 缓存30秒


def get_dashboard_stats(use_cache=True):
    """获取仪表盘统计数据 - 优化版（支持缓存）"""
    current_time = time.time()

    # 检查缓存
    if use_cache and _stats_cache['data'] and (current_time - _stats_cache['timestamp']) < _CACHE_TTL:
        return _stats_cache['data']

    # 重新查询数据库
    try:
        # 使用单次查询获取所有用户统计
        user_stats = db.session.query(
            func.count(User.id).label('total'),
            func.sum(func.cast(User.is_active, db.Integer)).label('active'),
            func.sum(func.cast(User.is_admin, db.Integer)).label('admin')
        ).first()

        # 计算活跃用户数（is_active=True的行数）
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()

        # 资产统计 - 使用单次查询
        asset_categories = db.session.query(
            DigitalAsset.category,
            func.count(DigitalAsset.id)
        ).group_by(DigitalAsset.category).all()
        total_assets = sum(count for _, count in asset_categories)
        asset_stats = {cat: count for cat, count in asset_categories}

        # 遗嘱统计 - 使用单次查询
        will_stats = db.session.query(
            DigitalWill.status,
            func.count(DigitalWill.id)
        ).group_by(DigitalWill.status).all()
        total_wills = sum(count for _, count in will_stats)
        will_status = {status: count for status, count in will_stats}

        # 内容统计 - 分别查询避免笛卡尔积
        policies_count = PlatformPolicy.query.count()
        faqs_count = FAQ.query.count()
        stories_count = Story.query.count()

        # 周统计
        week_ago = get_china_time() - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        active_users_week = User.query.filter(
            User.updated_at >= week_ago,
            User.is_active == True
        ).count()
        
        # 待审核故事
        pending_stories = Story.query.filter_by(status='pending').count()

        data = {
            'users': {
                'total': user_stats.total or 0,
                'active': active_users,
                'admin': admin_users,
                'new_week': new_users_week,
                'active_week': active_users_week
            },
            'assets': {
                'total': total_assets,
                'by_category': asset_stats
            },
            'wills': {
                'total': total_wills,
                'by_status': will_status
            },
            'content': {
                'policies': policies_count,
                'faqs': faqs_count,
                'stories': stories_count,
                'pending_stories': pending_stories
            }
        }

        # 更新缓存
        _stats_cache['data'] = data
        _stats_cache['timestamp'] = current_time

        return data
    except Exception as e:
        print(f"[ERROR] get_dashboard_stats failed: {e}")
        import traceback
        traceback.print_exc()
        # 返回空数据避免页面崩溃
        return {
            'users': {'total': 0, 'active': 0, 'admin': 0, 'new_week': 0, 'active_week': 0},
            'assets': {'total': 0, 'by_category': {}},
            'wills': {'total': 0, 'by_status': {}},
            'content': {'policies': 0, 'faqs': 0, 'stories': 0, 'pending_stories': 0}
        }


def get_user_growth_data(days=30):
    """获取用户增长数据（按天）"""
    dates = []
    counts = []

    for i in range(days):
        date = get_china_time() - timedelta(days=days - i - 1)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count = User.query.filter(
            User.created_at >= start_of_day,
            User.created_at <= end_of_day
        ).count()

        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)

    return {
        'dates': dates,
        'counts': counts
    }


def get_activity_data(days=7):
    """获取用户活动数据"""
    dates = []
    user_registrations = []
    asset_created = []
    will_created = []

    for i in range(days):
        date = get_china_time() - timedelta(days=days - i - 1)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # 新注册用户
        new_users = User.query.filter(
            User.created_at >= start_of_day,
            User.created_at <= end_of_day
        ).count()

        # 新建资产
        new_assets = DigitalAsset.query.filter(
            DigitalAsset.created_at >= start_of_day,
            DigitalAsset.created_at <= end_of_day
        ).count()

        # 新建遗嘱
        new_wills = DigitalWill.query.filter(
            DigitalWill.created_at >= start_of_day,
            DigitalWill.created_at <= end_of_day
        ).count()

        dates.append(date.strftime('%m-%d'))
        user_registrations.append(new_users)
        asset_created.append(new_assets)
        will_created.append(new_wills)

    return {
        'dates': dates,
        'user_registrations': user_registrations,
        'asset_created': asset_created,
        'will_created': will_created
    }


def get_category_distribution():
    """获取资产分类分布"""
    categories = db.session.query(
        DigitalAsset.category,
        func.count(DigitalAsset.id)
    ).group_by(DigitalAsset.category).all()

    labels = []
    data = []

    for cat, count in categories:
        labels.append(cat)
        data.append(count)

    return {
        'labels': labels,
        'data': data
    }
