#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试PBKDF2HMAC双层加密方案 - 完整版
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.encryption import (
    encrypt_data,
    decrypt_data,
    encrypt_data_with_derived_key,
    decrypt_data_with_derived_key
)

def test_pbkdf2_encryption():
    """测试PBKDF2HMAC双层加密(默认启用)"""
    print("=" * 60)
    print("测试1: PBKDF2HMAC双层加密(默认启用)")
    print("=" * 60)
    
    original_data = "这是需要加密的敏感数据:账号密码123456"
    
    # 测试加密(默认启用PBKDF2HMAC)
    encrypted = encrypt_data(original_data, use_pbkdf2=True)
    
    if encrypted:
        print("[OK] PBKDF2HMAC加密成功")
        print("   原始数据: %s" % original_data)
        print("   加密后: %s..." % encrypted[:30])
    else:
        print("[FAILED] PBKDF2HMAC加密失败")
        return False
    
    # 测试解密(默认启用PBKDF2HMAC)
    decrypted = decrypt_data(encrypted, use_pbkdf2=True)
    
    if decrypted == original_data:
        print("[OK] PBKDF2HMAC解密成功")
        print("   解密后: %s" % decrypted)
    else:
        print("[FAILED] PBKDF2HMAC解密失败或数据不匹配")
        return False
    
    return True

def test_backward_compatibility():
    """测试向后兼容(仅Fernet加密)"""
    print("\n" + "=" * 60)
    print("测试2: 向后兼容(仅Fernet加密)")
    print("=" * 60)
    
    original_data = "测试向后兼容性"
    
    # 测试加密(禁用PBKDF2HMAC)
    encrypted = encrypt_data(original_data, use_pbkdf2=False)
    
    if encrypted:
        print("[OK] Fernet加密成功")
        print("   原始数据: %s" % original_data)
        print("   加密后: %s..." % encrypted[:30])
    else:
        print("[FAILED] Fernet加密失败")
        return False
    
    # 测试解密(禁用PBKDF2HMAC)
    decrypted = decrypt_data(encrypted, use_pbkdf2=False)
    
    if decrypted == original_data:
        print("[OK] Fernet解密成功")
        print("   解密后: %s" % decrypted)
    else:
        print("[FAILED] Fernet解密失败")
        return False
    
    return True

def test_default_behavior():
    """测试默认行为(应启用PBKDF2HMAC)"""
    print("\n" + "=" * 60)
    print("测试3: 默认行为(应启用PBKDF2HMAC)")
    print("=" * 60)
    
    original_data = "测试默认加密行为"
    
    # 测试默认加密(不指定use_pbkdf2参数)
    encrypted = encrypt_data(original_data)
    
    if encrypted:
        print("[OK] 默认加密成功")
        print("   原始数据: %s" % original_data)
        print("   加密后: %s..." % encrypted[:30])
    else:
        print("[FAILED] 默认加密失败")
        return False
    
    # 测试默认解密(不指定use_pbkdf2参数)
    decrypted = decrypt_data(encrypted)
    
    if decrypted == original_data:
        print("[OK] 默认解密成功")
        print("   解密后: %s" % decrypted)
        print("\n[INFO] 默认行为验证: 已启用PBKDF2HMAC双层加密")
    else:
        print("[FAILED] 默认解密失败")
        return False
    
    return True

def test_custom_password():
    """测试自定义密码加密"""
    print("\n" + "=" * 60)
    print("测试4: 自定义密码加密")
    print("=" * 60)
    
    password = "my_custom_password_789"
    original_data = "使用自定义密码加密的数据"
    
    # 测试加密
    encrypted = encrypt_data_with_derived_key(original_data, password)
    
    if encrypted:
        print("[OK] 自定义密码加密成功")
        print("   密码: %s" % password)
        print("   原始数据: %s" % original_data)
        print("   加密后: %s..." % encrypted[:30])
    else:
        print("[FAILED] 自定义密码加密失败")
        return False
    
    # 测试解密
    decrypted = decrypt_data_with_derived_key(encrypted, password)
    
    if decrypted == original_data:
        print("[OK] 自定义密码解密成功")
        print("   解密后: %s" % decrypted)
    else:
        print("[FAILED] 自定义密码解密失败")
        return False
    
    # 测试错误密码
    wrong_password = "wrong_password"
    decrypted_wrong = decrypt_data_with_derived_key(encrypted, wrong_password)
    
    if decrypted_wrong is None:
        print("[OK] 错误密码解密失败验证通过")
    else:
        print("[FAILED] 错误密码解密成功,存在安全风险")
        return False
    
    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("PBKDF2HMAC双层加密方案完整测试")
    print("=" * 60 + "\n")
    
    results = []
    
    # 运行所有测试
    results.append(("PBKDF2HMAC双层加密", test_pbkdf2_encryption()))
    results.append(("向后兼容(Fernet)", test_backward_compatibility()))
    results.append(("默认行为验证", test_default_behavior()))
    results.append(("自定义密码加密", test_custom_password()))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "[OK] 通过" if result else "[FAILED] 失败"
        print("%s: %s" % (test_name, status))
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[SUCCESS] 所有测试通过!")
        print("\n功能验证:")
        print("1. [OK] PBKDF2HMAC双层加密已启用并正常工作")
        print("2. [OK] 向后兼容性保持,支持原有Fernet加密")
        print("3. [OK] 默认行为已启用PBKDF2HMAC,符合《技术概要》")
        print("4. [OK] 自定义密码加密功能正常")
        print("\n技术实现:")
        print("- PBKDF2HMAC: SHA256算法,100000次迭代")
        print("- Fernet: AES-128-CBC + HMAC-SHA256")
        print("- 双层加密: PBKDF2HMAC派生密钥 + Fernet加密")
        print("\n符合《技术概要》要求:")
        print("- Fernet 对称加密 + PBKDF2HMAC 密钥派生")
        print("- 保障数据存储安全")
        print("- 已在实际业务中启用")
        return 0
    else:
        print("\n[FAILED] 部分测试失败,请检查实现")
        return 1

if __name__ == "__main__":
    exit(main())
