#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试PBKDF2HMAC密钥派生功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.encryption import (
    derive_key_from_password,
    encrypt_data_with_derived_key,
    decrypt_data_with_derived_key,
    encrypt_data,
    decrypt_data
)

def test_pbkdf2_key_derivation():
    """测试PBKDF2HMAC密钥派生"""
    print("=" * 60)
    print("测试1: PBKDF2HMAC密钥派生")
    print("=" * 60)
    
    password = "test_password_123"
    
    # 测试密钥派生
    derived_key = derive_key_from_password(password)
    
    if derived_key:
        print("[OK] 密钥派生成功")
        print("   密码: %s" % password)
        print("   派生密钥: %s..." % derived_key[:20])
        print("   密钥长度: %d 字节" % len(derived_key))
    else:
        print("[FAILED] 密钥派生失败")
        return False
    
    # 测试相同密码派生相同密钥
    derived_key2 = derive_key_from_password(password)
    if derived_key == derived_key2:
        print("[OK] 相同密码派生相同密钥验证通过")
    else:
        print("[FAILED] 相同密码派生不同密钥,验证失败")
        return False
    
    # 测试不同密码派生不同密钥
    password2 = "different_password"
    derived_key3 = derive_key_from_password(password2)
    if derived_key != derived_key3:
        print("[OK] 不同密码派生不同密钥验证通过")
    else:
        print("[FAILED] 不同密码派生相同密钥,验证失败")
        return False
    
    return True

def test_double_encryption():
    """测试双层加密方案(Fernet + PBKDF2HMAC)"""
    print("\n" + "=" * 60)
    print("测试2: 双层加密方案")
    print("=" * 60)
    
    password = "user_password_456"
    original_data = "这是需要加密的敏感数据:账号密码123456"
    
    # 测试加密
    encrypted = encrypt_data_with_derived_key(original_data, password)
    
    if encrypted:
        print("[OK] 加密成功")
        print("   原始数据: %s" % original_data)
        print("   加密后: %s..." % encrypted[:30])
    else:
        print("[FAILED] 加密失败")
        return False
    
    # 测试解密
    decrypted = decrypt_data_with_derived_key(encrypted, password)
    
    if decrypted == original_data:
        print("[OK] 解密成功")
        print("   解密后: %s" % decrypted)
    else:
        print("[FAILED] 解密失败或数据不匹配")
        return False
    
    # 测试错误密码解密
    wrong_password = "wrong_password"
    decrypted_wrong = decrypt_data_with_derived_key(encrypted, wrong_password)
    
    if decrypted_wrong is None:
        print("[OK] 错误密码解密失败验证通过")
    else:
        print("[FAILED] 错误密码解密成功,存在安全风险")
        return False
    
    return True

def test_original_encryption():
    """测试原有Fernet加密功能(确保向后兼容)"""
    print("\n" + "=" * 60)
    print("测试3: 原有Fernet加密功能(向后兼容)")
    print("=" * 60)
    
    original_data = "测试原有加密功能"
    
    # 测试原有加密
    encrypted = encrypt_data(original_data)
    
    if encrypted:
        print("[OK] 原有加密成功")
        print("   原始数据: %s" % original_data)
        print("   加密后: %s..." % encrypted[:30])
    else:
        print("[FAILED] 原有加密失败")
        return False
    
    # 测试原有解密
    decrypted = decrypt_data(encrypted)
    
    if decrypted == original_data:
        print("[OK] 原有解密成功")
        print("   解密后: %s" % decrypted)
    else:
        print("[FAILED] 原有解密失败")
        return False
    
    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("PBKDF2HMAC密钥派生功能测试")
    print("=" * 60 + "\n")
    
    results = []
    
    # 运行所有测试
    results.append(("PBKDF2HMAC密钥派生", test_pbkdf2_key_derivation()))
    results.append(("双层加密方案", test_double_encryption()))
    results.append(("原有Fernet加密", test_original_encryption()))
    
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
        print("\n[SUCCESS] 所有测试通过! PBKDF2HMAC功能已成功实现!")
        print("\n技术实现说明:")
        print("1. [OK] PBKDF2HMAC密钥派生: 使用SHA256算法,100000次迭代")
        print("2. [OK] 双层加密方案: PBKDF2HMAC派生密钥 + Fernet对称加密")
        print("3. [OK] 向后兼容: 原有Fernet加密功能保持不变")
        print("\n符合《技术概要》要求:")
        print("- Fernet 对称加密 + PBKDF2HMAC 密钥派生")
        print("- 保障数据存储安全")
        return 0
    else:
        print("\n[FAILED] 部分测试失败,请检查实现")
        return 1

if __name__ == "__main__":
    exit(main())
