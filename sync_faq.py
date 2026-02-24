"""FAQ数据同步工具"""
import json
from datetime import datetime
from models import db, FAQ
from app import app

def export_faq_to_json():
    """导出FAQ数据为JSON格式"""
    export_data = {
        'faqs': [],
        'export_time': datetime.now().isoformat()
    }

    with app.app_context():
        faqs = FAQ.query.all()
        for faq in faqs:
            export_data['faqs'].append({
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category,
                'order': faq.order
            })

    return export_data

def import_json_to_database(data):
    """从JSON导入数据到数据库"""
    with app.app_context():
        print(f"\n开始导入FAQ数据...")
        imported_count = 0
        updated_count = 0

        for faq_data in data.get('faqs', []):
            # 检查是否已存在
            existing = FAQ.query.filter_by(id=faq_data['id']).first()

            if existing:
                # 更新现有记录
                existing.question = faq_data['question']
                existing.answer = faq_data['answer']
                existing.category = faq_data.get('category', '通用')
                existing.order = faq_data.get('order', 0)
                updated_count += 1
            else:
                # 创建新记录
                faq = FAQ(
                    id=faq_data['id'],
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    category=faq_data.get('category', '通用'),
                    order=faq_data.get('order', 0)
                )
                db.session.add(faq)
                imported_count += 1

        try:
            db.session.commit()
            print(f"✅ 成功:")
            print(f"   - 新增: {imported_count} 条")
            print(f"   - 更新: {updated_count} 条")
            print(f"   - 总计: {imported_count + updated_count} 条")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 导入失败: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("FAQ数据同步工具")
    print("=" * 60)

    # 导出数据
    print("\n📤 正在导出FAQ数据...")
    export_data = export_faq_to_json()

    print(f"\n导出统计:")
    print(f"  - FAQ数量: {len(export_data['faqs'])}")

    # 保存到文件
    filename = f"faq_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 数据已导出到: {filename}")

    # 导入FAQ数据
    print("\n" + "=" * 60)
    import_json_to_database(export_data)

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
