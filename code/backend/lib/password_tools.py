from backend.settings import config_data

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import base64

def aes_encrypt_password(password):
    """使用 AES 加密密码"""
    # 生成密钥（确保密钥长度为 16 字节）
    key = config_data.get('AES_KEY')
    key = key[:16].encode() if len(key) >= 16 else key.ljust(16).encode()

    # 生成随机初始化向量 (IV)
    iv = os.urandom(16)

    # 填充密码到块大小的倍数
    padded_password = pad(password.encode(), AES.block_size)

    # 加密密码
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_password = cipher.encrypt(padded_password)

    # 返回 Base64 编码的 IV 和加密结果
    return base64.b64encode(iv + encrypted_password).decode()


def aes_decrypt_password(encrypted_password):
    """使用 AES 解密密码"""
    key = config_data.get('AES_KEY')
    key = key[:16].encode() if len(key) >= 16 else key.ljust(16).encode()
    encrypted_data = base64.b64decode(encrypted_password)
    iv = encrypted_data[:16]
    encrypted_password = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_password = cipher.decrypt(encrypted_password)
    return unpad(padded_password, AES.block_size).decode()
