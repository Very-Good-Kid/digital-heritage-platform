#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新平台政策数据，使其与前端 /inheritance 页面的静态内容一致
"""

from app import app, db
from models import PlatformPolicy

def update_policies():
    with app.app_context():
        # 定义正确的政策数据（与前端 /inheritance 页面一致）
        correct_policies = {
            'QQ': {
                'policy_content': '账号本身不可被继承；账号内财产可被继承',
                'attitude': '明确禁止',  # 前端显示账号不可继承
                'inherit_possibility': '低',
                'customer_service': '综合热线：4006-700-700（9:00-22:00）；在线联系：腾讯客服公众号/小程序、网站kf.qq.com；本地备用：0755-83765566',
                'legal_basis': '《QQ号码规则》规定QQ号码所有权属于腾讯，使用权仅属于初始申请注册人，明确禁止继承。',
                'risk_warning': 'QQ账号长期未登录可能被回收，继承人可能永久失去访问渠道。'
            },
            '微信': {
                'policy_content': '账号本身不可被继承；账号内财产可被继承',
                'attitude': '明确禁止',  # 前端显示账号不可继承
                'inherit_possibility': '低',
                'customer_service': '客服热线：95017；在线联系：微信APP内「我-设置-帮助与反馈」、微信/QQ端「腾讯客服」小程序',
                'legal_basis': '《腾讯微信软件许可及服务协议》规定微信账号所有权归腾讯，使用权仅属于初始申请注册人，明确禁止继承。',
                'risk_warning': '微信零钱余额需凭公证遗嘱、继承权公证书等向财付通公司申请提取。'
            },
            '抖音': {
                'policy_content': '账号本身原则上不可继承，但司法实践已有突破；账号内财产可被继承；逝者个人信息可依法复制/下载/转移',
                'attitude': '有限支持',  # 前端显示司法实践有突破
                'inherit_possibility': '中',  # 前端显示中等
                'customer_service': '客服热线：95152；在线联系：抖音APP内「我-≡-我的客服」、微信/QQ端搜索抖音公众号；官方邮箱：feedback@douyin.com',
                'legal_basis': '《抖音隐私政策》3.5条规定逝者近亲属可依法行使个人信息相关权利，账号可设为纪念账号。',
                'risk_warning': '逝者近亲属需提交身份证明、死亡证明、亲属关系证明等材料完成核验。'
            }
        }

        # 更新数据库中的政策
        for platform_name, data in correct_policies.items():
            policy = PlatformPolicy.query.filter_by(platform_name=platform_name).first()
            if policy:
                policy.policy_content = data['policy_content']
                policy.attitude = data['attitude']
                policy.inherit_possibility = data['inherit_possibility']
                policy.customer_service = data['customer_service']
                policy.legal_basis = data['legal_basis']
                policy.risk_warning = data['risk_warning']
                print(f"已更新 {platform_name} 的政策数据")
            else:
                # 如果不存在，创建新记录
                new_policy = PlatformPolicy(
                    platform_name=platform_name,
                    policy_content=data['policy_content'],
                    attitude=data['attitude'],
                    inherit_possibility=data['inherit_possibility'],
                    customer_service=data['customer_service'],
                    legal_basis=data['legal_basis'],
                    risk_warning=data['risk_warning']
                )
                db.session.add(new_policy)
                print(f"已创建 {platform_name} 的政策数据")

        # 删除测试数据
        test_policy = PlatformPolicy.query.filter_by(platform_name='test').first()
        if test_policy:
            db.session.delete(test_policy)
            print("已删除测试数据")

        db.session.commit()
        print("\n政策数据更新完成！")

if __name__ == '__main__':
    update_policies()
