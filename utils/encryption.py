"""
加密工具模块 - 支持PBKDF2HMAC密钥派生的双层加密方案（安全加固版）

技术实现:
1. Fernet对称加密: 使用AES-128-CBC模式进行数据加密
2. PBKDF2HMAC密钥派生: 使用SHA256算法,600000次迭代,从密码派生加密密钥
3. 每条记录使用随机盐（salt随密文存储），消除全局固定盐风险

安全特性（v2 加固）:
- 缺失 ENCRYPTION_KEY / ENCRYPTION_PASSWORD 时 **fail-fast 拒绝启动**（禁止默认值）
- 每条记录独立随机盐（os.urandom(16)），盐随密文存储，消除全局固定盐风险
- 密钥绝不打印到日志，异常仅记录错误类型
- PBKDF2 迭代次数 600000（OWASP 2023+ 推荐量级）

使用方式:
- encrypt_data(data): 加密数据（自动生成随机盐，返回 salt_b64:cipher_b64）
- decrypt_data(encrypted_data): 解密数据（从密文中提取盐值）
- encrypt_data_with_derived_key(data, password, salt): 使用自定义密码+显式盐加密
- decrypt_data_with_derived_key(payload, password): 使用自定义密码解密

环境变量:
- ENCRYPTION_KEY: Fernet加密密钥（必须设置，缺失则拒绝启动）
- ENCRYPTION_PASSWORD: PBKDF2HMAC主密码（必须设置，缺失则拒绝启动）
"""

import base64
import binascii
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ============================================================
# 加密配置 —— 缺失即 fail-fast，禁止任何默认值
# ============================================================

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise RuntimeError(
        "ENCRYPTION_KEY 未设置：拒绝启动。请通过密钥管理服务/部署平台注入 Fernet 密钥。"
    )
try:
    fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
except (ValueError, TypeError):
    raise RuntimeError(
        "ENCRYPTION_KEY 格式非法：必须为合法 Fernet 密钥（base64, 44 字符）。"
    )

ENCRYPTION_PASSWORD = os.environ.get('ENCRYPTION_PASSWORD')
if not ENCRYPTION_PASSWORD:
    raise RuntimeError(
        "ENCRYPTION_PASSWORD 未设置：拒绝启动。请通过密钥管理服务/部署平台注入。"
    )

# OWASP 2023+ 推荐：PBKDF2-SHA256 迭代 ≥ 600000
PBKDF2_ITERATIONS = 600000


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """使用PBKDF2HMAC从密码派生加密密钥。

    salt 必须显式传入（每条记录独立随机盐），不再使用全局固定盐。

    Returns:
        派生出的32字节密钥（base64 编码，适合 Fernet 使用）
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_data_with_derived_key(data: str, password: str, salt: bytes) -> str:
    """使用PBKDF2HMAC派生密钥后加密数据。

    返回格式: salt_b64:cipher_b64（盐随密文一起存储）
    """
    if not data or not password:
        return None

    derived_key = derive_key_from_password(password, salt)
    fernet_derived = Fernet(derived_key)
    encrypted = fernet_derived.encrypt(data.encode())
    return (
        base64.urlsafe_b64encode(salt).decode()
        + ':'
        + base64.urlsafe_b64encode(encrypted).decode()
    )


def decrypt_data_with_derived_key(payload: str, password: str) -> str:
    """使用PBKDF2HMAC派生密钥后解密数据。

    从 payload 的 salt_b64:cipher_b64 中提取盐值。
    """
    if not payload or not password:
        return None

    try:
        salt_b64, cipher_b64 = payload.split(':', 1)
        salt = base64.urlsafe_b64decode(salt_b64)
        derived_key = derive_key_from_password(password, salt)
        return (
            Fernet(derived_key)
            .decrypt(base64.urlsafe_b64decode(cipher_b64))
            .decode()
        )
    except (InvalidToken, ValueError, binascii.Error) as e:
        # 安全：不打印密钥/敏感信息，仅记录错误类型
        raise ValueError("解密失败：密钥不匹配或数据损坏") from e


def encrypt_data(data: str, salt: bytes = None) -> str:
    """对外加密接口。每条记录使用独立随机盐。

    Args:
        data: 要加密的字符串数据
        salt: 可选随机盐（16字节），不传则自动生成 os.urandom(16)

    Returns:
        salt_b64:cipher_b64 格式的密文字符串
    """
    if not data:
        return None

    if salt is None:
        salt = os.urandom(16)

    return encrypt_data_with_derived_key(data, ENCRYPTION_PASSWORD, salt)


def decrypt_data(encrypted_data: str) -> str:
    """对外解密接口。

    Args:
        encrypted_data: salt_b64:cipher_b64 格式的密文字符串

    Returns:
        解密后的原始字符串，失败返回 None
    """
    if not encrypted_data:
        return None

    try:
        return decrypt_data_with_derived_key(encrypted_data, ENCRYPTION_PASSWORD)
    except ValueError:
        return None
