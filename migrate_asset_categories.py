"""
迁移数字资产分类 - 将旧分类更新为新分类
"""
from app import app, db
from models import DigitalAsset


def migrate_asset_categories():
    """迁移数字资产分类"""
    with app.app_context():
        # 分类映射
        category_mapping = {
            '社交': '社交媒体',
            '金融': '电子邮箱',
            '记忆': '云存储与数字内容',
            '虚拟财产': '虚拟资产与数字货币'
        }

        updated_count = 0
        for old_cat, new_cat in category_mapping.items():
            assets = DigitalAsset.query.filter_by(category=old_cat).all()
            if assets:
                print(f'更新 {old_cat} -> {new_cat}: {len(assets)}个资产')
                for asset in assets:
                    asset.category = new_cat
                db.session.commit()
                updated_count += len(assets)

        print(f'\n分类迁移完成，共更新 {updated_count} 个资产')

        # 显示当前分类统计
        print('\n当前数据库中的分类:')
        assets = DigitalAsset.query.all()
        categories = set(asset.category for asset in assets)
        for cat in sorted(categories):
            count = DigitalAsset.query.filter_by(category=cat).count()
            print(f'  {cat}: {count}个')


if __name__ == '__main__':
    migrate_asset_categories()
