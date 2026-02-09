from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# 使用环境变量中的密钥或生成新的密钥
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # 在生产环境中，这个密钥应该安全地存储
    ENCRYPTION_KEY = Fernet.generate_key()
    print(f"Generated encryption key: {ENCRYPTION_KEY.decode()}")

fernet = Fernet(ENCRYPTION_KEY)

def encrypt_data(data):
    """
    加密数据

    Args:
        data: 要加密的字符串数据

    Returns:
        加密后的字符串
    """
    if not data:
        return None
    try:
        encrypted = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_data(encrypted_data):
    """
    解密数据

    Args:
        encrypted_data: 加密的字符串数据

    Returns:
        解密后的原始字符串
    """
    if not encrypted_data:
        return None
    try:
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
