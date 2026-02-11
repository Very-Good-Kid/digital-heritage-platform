#!/usr/bin/env python3
"""
更新 FAQ 数据脚本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FAQ

def update_faqs():
    """更新 FAQ 数据"""
    with app.app_context():
        # 删除所有现有 FAQ
        FAQ.query.delete()
        db.session.commit()
        print("已删除所有现有 FAQ")

        # 添加新的 FAQ
        faqs = [
            FAQ(
                question='数字遗产包括哪些内容？',
                answer='数字遗产包括但不限于：社交媒体账号（微信、QQ、抖音等）、电子邮箱、云存储文件、虚拟货币、游戏账号、在线支付账户、博客文章、个人网站、数字相册、音视频文件等。',
                category='基础概念',
                order=1
            ),
            FAQ(
                question='什么是数字遗嘱？',
                answer='数字遗嘱是指用户在生前制定的关于其数字资产如何处理的书面文件，包括账户信息、密码、处理方式等内容的详细说明。它可以指导继承人如何处理您的数字资产，避免账户丢失或数据永久消失。',
                category='基础概念',
                order=2
            ),
            FAQ(
                question='为什么需要规划数字遗产？',
                answer='1. 避免重要数据永久丢失；2. 保护隐私和个人信息；3. 确保资产（如虚拟货币）不被浪费；4. 减轻家人的心理负担；5. 让数字记忆得以传承；6. 避免平台账户被自动删除。',
                category='基础概念',
                order=3
            ),
            FAQ(
                question='数字资产的价值如何评估？',
                answer='数字资产的价值包括：经济价值（虚拟货币、游戏装备、付费内容等）、情感价值（照片、视频、聊天记录等）、实用价值（付费软件、云存储空间等）。建议定期整理和评估您的数字资产。',
                category='基础概念',
                order=4
            ),
            FAQ(
                question='如何保护我的数字遗产？',
                answer='1. 定期备份重要数据到本地或云端；2. 使用密码管理器安全存储密码；3. 创建数字遗嘱并定期更新；4. 告知家人重要账户信息；5. 了解各平台的继承政策；6. 启用双重认证；7. 定期检查账户安全设置。',
                category='保护措施',
                order=1
            ),
            FAQ(
                question='密码安全应该注意什么？',
                answer='1. 使用强密码（大小写字母、数字、特殊符号组合，至少12位）；2. 不要重复使用密码；3. 定期更换密码（每3-6个月）；4. 启用两步验证；5. 使用密码管理器（如LastPass、1Password）；6. 不要在公共场所输入密码；7. 警惕钓鱼网站。',
                category='保护措施',
                order=2
            ),
            FAQ(
                question='如何选择密码管理器？',
                answer='选择密码管理器时考虑：1. 安全性（是否使用AES-256加密）；2. 跨平台支持（手机、电脑、浏览器）；3. 云同步功能；4. 价格（免费版功能）；5. 用户评价和口碑。推荐工具：LastPass、1Password、Bitwarden、KeePass等。',
                category='保护措施',
                order=3
            ),
            FAQ(
                question='数字遗嘱有法律效力吗？',
                answer='数字遗嘱在我国法律体系中尚未明确认定，但可以作为表达意愿的重要依据。根据《民法典》，遗嘱可以采用多种形式，包括打印、录音录像等。数字遗嘱如果能证明是本人真实意愿，可能被参考。建议配合传统遗嘱使用，并咨询专业律师。',
                category='法律问题',
                order=1
            ),
            FAQ(
                question='继承人的法律权利是什么？',
                answer='根据《民法典》，继承人有权继承被继承人的合法财产。但对于数字财产，法律界定尚不明确：1. 虚拟货币（比特币等）通常被视为财产，可以继承；2. 社交媒体账号（微信、QQ等）通常被视为使用权，不可继承；3. 游戏账号和虚拟道具的继承权取决于平台政策；4. 云存储文件可以继承，但需要密码或法律证明。',
                category='法律问题',
                order=2
            ),
            FAQ(
                question='如何证明数字资产的所有权？',
                answer='证明数字资产所有权需要：1. 账户注册信息和登录记录；2. 交易记录和支付凭证（如购买虚拟货币的记录）；3. 电子邮件或聊天记录证明使用情况；4. 平台开具的资产证明；5. 公证处的公证文件；6. 银行流水证明充值记录。建议保留所有相关凭证。',
                category='法律问题',
                order=3
            ),
            FAQ(
                question='如果平台拒绝继承怎么办？',
                answer='1. 查阅平台服务协议，了解具体条款；2. 准备完整的法律文件（死亡证明、继承公证书等）；3. 联系平台客服，说明情况；4. 寻求法律援助，向法院提起诉讼；5. 向消费者协会投诉；6. 通过媒体曝光引起关注。注意：不同平台处理方式不同，需要具体情况具体分析。',
                category='法律问题',
                order=4
            ),
            FAQ(
                question='跨境数字资产继承有什么特殊问题？',
                answer='1. 法律适用问题：涉及不同国家的法律；2. 语言障碍：需要翻译文件；3. 货币兑换：虚拟货币可能需要兑换；4. 税务问题：可能涉及遗产税；5. 时效问题：各国继承时效不同；6. 证据认证：需要领事认证或海牙认证。建议咨询专业国际律师。',
                category='法律问题',
                order=5
            )
        ]

        for faq in faqs:
            db.session.add(faq)

        db.session.commit()
        print(f"成功添加 {len(faqs)} 个 FAQ")

        # 验证
        count = FAQ.query.count()
        print(f"当前 FAQ 总数: {count}")

        # 按分类统计
        categories = {}
        for faq in FAQ.query.all():
            if faq.category not in categories:
                categories[faq.category] = 0
            categories[faq.category] += 1

        print("\n按分类统计:")
        for category, count in categories.items():
            print(f"  {category}: {count} 个")

if __name__ == '__main__':
    update_faqs()
    print("\nFAQ 更新完成！")
