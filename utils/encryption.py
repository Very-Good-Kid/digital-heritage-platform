"""
加密工具模块 - 支持PBKDF2HMAC密钥派生的双层加密方案

技术实现:
1. Fernet对称加密: 使用AES-128-CBC模式进行数据加密
2. PBKDF2HMAC密钥派生: 使用SHA256算法,100000次迭代,从密码派生加密密钥
3. 双层加密方案: PBKDF2HMAC派生密钥 + Fernet加密,符合《技术概要》要求

安全特性:
- 密钥派生强度: 100000次PBKDF2HMAC迭代,抗暴力破解
- 加密算法: Fernet(AES-128-CBC + HMAC-SHA256)
- 向后兼容: 支持原有Fernet加密方式

使用方式:
- encrypt_data(data, use_pbkdf2=True): 加密数据(默认启用PBKDF2HMAC)
- decrypt_data(encrypted_data, use_pbkdf2=True): 解密数据(默认启用PBKDF2HMAC)
- encrypt_data_with_derived_key(data, password): 使用自定义密码加密
- decrypt_data_with_derived_key(encrypted_data, password): 使用自定义密码解密

环境变量:
- ENCRYPTION_KEY: Fernet加密密钥(可选,不设置则自动生成)
- ENCRYPTION_PASSWORD: PBKDF2HMAC密码(可选,不设置则使用默认密码)
- PBKDF2_SALT: PBKDF2HMAC盐值(可选,不设置则使用默认盐值)
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# ============================================================
# 加密配置
# ============================================================

# Fernet加密密钥(用于向后兼容的单层加密)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # 在生产环境中，这个密钥应该安全地存储
    ENCRYPTION_KEY = Fernet.generate_key()
    print(f"Generated encryption key: {ENCRYPTION_KEY.decode()}")

fernet = Fernet(ENCRYPTION_KEY)

# PBKDF2HMAC密钥派生相关
# 使用固定的盐值（生产环境应从环境变量获取）
PBKDF2_SALT = os.environ.get('PBKDF2_SALT', b'digital_heritage_platform_salt_2026')
PBKDF2_ITERATIONS = 100000  # 迭代次数，符合安全标准

def derive_key_from_password(password: str, salt: bytes = None) -> bytes:
    """
    使用PBKDF2HMAC从密码派生加密密钥
    
    Args:
        password: 用户密码或主密钥
        salt: 盐值，如果不提供则使用默认盐值
    
    Returns:
        派生出的32字节密钥（适合Fernet使用）
    """
    if salt is None:
        salt = PBKDF2_SALT
    
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet需要32字节密钥
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        derived_key = kdf.derive(password.encode())
        # 转换为Fernet可用的base64格式
        return base64.urlsafe_b64encode(derived_key)
    except Exception as e:
        print(f"Key derivation error: {e}")
        return None

def encrypt_data_with_derived_key(data: str, password: str) -> str:
    """
    使用PBKDF2HMAC派生密钥后加密数据（双层加密方案）
    
    Args:
        data: 要加密的字符串数据
        password: 用于派生密钥的密码
    
    Returns:
        加密后的字符串
    """
    if not data or not password:
        return None
    
    try:
        # 第一步：使用PBKDF2HMAC从密码派生密钥
        derived_key = derive_key_from_password(password)
        if not derived_key:
            return None
        
        # 第二步：使用派生密钥创建Fernet实例进行加密
        fernet_derived = Fernet(derived_key)
        encrypted = fernet_derived.encrypt(data.encode())
        
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        print(f"Encryption with derived key error: {e}")
        return None

def decrypt_data_with_derived_key(encrypted_data: str, password: str) -> str:
    """
    使用PBKDF2HMAC派生密钥后解密数据（双层加密方案）
    
    Args:
        encrypted_data: 加密的字符串数据
        password: 用于派生密钥的密码
    
    Returns:
        解密后的原始字符串
    """
    if not encrypted_data or not password:
        return None
    
    try:
        # 第一步：使用PBKDF2HMAC从密码派生密钥
        derived_key = derive_key_from_password(password)
        if not derived_key:
            return None
        
        # 第二步：使用派生密钥创建Fernet实例进行解密
        fernet_derived = Fernet(derived_key)
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet_derived.decrypt(decoded)
        
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption with derived key error: {e}")
        return None

def encrypt_data(data, use_pbkdf2=True):
    """
    加密数据 - 支持PBKDF2HMAC密钥派生的双层加密方案
    
    Args:
        data: 要加密的字符串数据
        use_pbkdf2: 是否使用PBKDF2HMAC密钥派生(默认True)
                   True: 使用PBKDF2HMAC派生密钥+Fernet加密(符合《技术概要》)
                   False: 仅使用Fernet加密(向后兼容)
    
    Returns:
        加密后的字符串
    """
    if not data:
        return None
    
    try:
        if use_pbkdf2:
            # 使用PBKDF2HMAC密钥派生(符合《技术概要》要求)
            # 使用环境变量中的密码或默认密码
            password = os.environ.get('ENCRYPTION_PASSWORD', 'digital_heritage_default_password_2026')
            return encrypt_data_with_derived_key(data, password)
        else:
            # 原有Fernet加密(向后兼容)
            encrypted = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_data(encrypted_data, use_pbkdf2='auto'):
    """
    解密数据 - 支持PBKDF2HMAC密钥派生的双层解密方案(自动检测加密方式)
    
    Args:
        encrypted_data: 加密的字符串数据
        use_pbkdf2: 是否使用PBKDF2HMAC密钥派生
                   'auto': 自动检测加密方式(默认,推荐)
                   True: 使用PBKDF2HMAC派生密钥+Fernet解密
                   False: 仅使用Fernet解密(向后兼容)
    
    Returns:
        解密后的原始字符串
    """
    if not encrypted_data:
        return None
    
    # 自动检测模式:先尝试PBKDF2HMAC,失败则尝试Fernet
    if use_pbkdf2 == 'auto':
        # 先尝试PBKDF2HMAC解密(新数据)
        try:
            password = os.environ.get('ENCRYPTION_PASSWORD', 'digital_heritage_default_password_2026')
            result = decrypt_data_with_derived_key(encrypted_data, password)
            if result:
                return result
        except:
            pass
        
        # 如果PBKDF2HMAC失败,尝试Fernet解密(旧数据)
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error (auto mode): {e}")
            return None
    
    # 手动指定模式
    try:
        if use_pbkdf2:
            # 使用PBKDF2HMAC密钥派生(符合《技术概要》要求)
            password = os.environ.get('ENCRYPTION_PASSWORD', 'digital_heritage_default_password_2026')
            return decrypt_data_with_derived_key(encrypted_data, password)
        else:
            # 原有Fernet解密(向后兼容)
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
