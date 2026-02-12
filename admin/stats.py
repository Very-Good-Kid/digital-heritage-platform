"""
后台管理系统 - 数据统计模块
"""
from datetime import datetime, timedelta
from sqlalchemy import func

from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ, get_china_time


def get_dashboard_stats():
    """获取仪表盘统计数据"""
    # 用户统计
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()

    # 资产统计
    total_assets = DigitalAsset.query.count()
    # 按分类统计
    asset_categories = db.session.query(
        DigitalAsset.category,
        func.count(DigitalAsset.id)
    ).group_by(DigitalAsset.category).all()
    asset_stats = {cat: count for cat, count in asset_categories}

    # 遗嘱统计
    total_wills = DigitalWill.query.count()
    will_stats = db.session.query(
        DigitalWill.status,
        func.count(DigitalWill.id)
    ).group_by(DigitalWill.status).all()
    will_status = {status: count for status, count in will_stats}

    # 内容统计
    total_policies = PlatformPolicy.query.count()
    total_faqs = FAQ.query.count()
    total_stories = Story.query.count()
    pending_stories = Story.query.filter_by(status='pending').count()

    # 最近注册用户（7天内）
    week_ago = get_china_time() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()

    # 最近活跃用户（7天内）
    # 假设updated_at表示用户最后活动时间
    active_users_week = User.query.filter(
        User.updated_at >= week_ago,
        User.is_active == True
    ).count()

    return {
        'users': {
            'total': total_users,
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
            'policies': total_policies,
            'faqs': total_faqs,
            'stories': total_stories,
            'pending_stories': pending_stories
        }
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
