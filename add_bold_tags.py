# -*- coding: utf-8 -*-
"""
为指定内容添加加粗效果
"""
import re

# 读取文件
with open('templates/inheritance/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义需要加粗的内容(微信)
wechat_bold_patterns = [
    (r'不受《存款保险条例》保护，', r'<strong>不受《存款保险条例》保护，</strong>'),
    (r'但不以你本人名义存放在银行，', r'<strong>但不以你本人名义存放在银行，</strong>'),
    (r'微信支付账户内的资金余额可作为遗产被继承。', r'<strong>微信支付账户内的资金余额可作为遗产被继承。</strong>'),
    (r'需凭公证遗嘱、继承权公证书', r'<strong>需凭公证遗嘱、继承权公证书</strong>'),
    (r'微信账号的所有权归腾讯公司所有，', r'<strong>微信账号的所有权归腾讯公司所有，</strong>'),
    (r'用户并非取得对该虚拟财产的物权，只是基于合同获得了平台服务的使用资格', r'<strong>用户并非取得对该虚拟财产的物权，只是基于合同获得了平台服务的使用资格</strong>'),
    (r'明确禁止初始注册人以赠与、转让等方式许可他人使用账号，也禁止非初始注册人通过继承、受赠等任何方式取得账号使用权', r'<strong>明确禁止初始注册人以赠与、转让等方式许可他人使用账号，也禁止非初始注册人通过继承、受赠等任何方式取得账号使用权</strong>'),
]

# 定义需要加粗的内容(QQ)
qq_bold_patterns = [
    (r'其所有权（物权）归属于腾讯公司，而非注册用户', r'<strong>其所有权（物权）归属于腾讯公司，而非注册用户</strong>'),
    (r'其所有权属于腾讯', r'<strong>其所有权属于腾讯</strong>'),
    (r'其继承人无法主张对 QQ 号码本身的所有权', r'<strong>其继承人无法主张对 QQ 号码本身的所有权</strong>'),
    (r'直接排除了微信功能账号使用权的流转可能，尤其是将"继承"明确列入禁止情形', r'<strong>直接排除了微信功能账号使用权的流转可能，尤其是将"继承"明确列入禁止情形</strong>'),
    (r'您不得赠与、借用、租用、转让或售卖 QQ 号码或者以其他方式许可非初始申请注册人使用 QQ 号码', r'<strong>您不得赠与、借用、租用、转让或售卖 QQ 号码或者以其他方式许可非初始申请注册人使用 QQ 号码</strong>'),
    (r'若用户停止使用服务，腾讯有权永久删除服务器上的用户数据，且无义务返还', r'<strong>若用户停止使用服务，腾讯有权永久删除服务器上的用户数据，且无义务返还</strong>'),
    (r'继承人可能永久失去访问该账号的渠道', r'<strong>继承人可能永久失去访问该账号的渠道</strong>'),
    (r'腾讯有权从服务器上永久地删除您的数据。您的服务停止、终止或取消后，腾讯没有义务向您返还任何数据', r'<strong>腾讯有权从服务器上永久地删除您的数据。您的服务停止、终止或取消后，腾讯没有义务向您返还任何数据</strong>'),
    (r'仅在法律法规要求、司法/行政机关调取、为完成资产转让或提供必要服务等少数情况下，腾讯才可向第三方披露用户信息', r'<strong>仅在法律法规要求、司法/行政机关调取、为完成资产转让或提供必要服务等少数情况下，腾讯才可向第三方披露用户信息</strong>'),
]

# 应用所有替换
all_patterns = wechat_bold_patterns + qq_bold_patterns
for pattern, replacement in all_patterns:
    content = re.sub(pattern, replacement, content)

# 写回文件
with open('templates/inheritance/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] 加粗效果添加完成!")
print(f"   - 微信平台: {len(wechat_bold_patterns)} 处")
print(f"   - QQ平台: {len(qq_bold_patterns)} 处")
print(f"   - 总计: {len(all_patterns)} 处")
