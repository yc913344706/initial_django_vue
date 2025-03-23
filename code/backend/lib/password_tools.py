from backend.settings import config_data
from lib.log import color_logger

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


from cryptography.hazmat.primitives import padding
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers import algorithms
from binascii import b2a_hex, a2b_hex

class AesCrypto(object):
    """
    加密解密
    """

    def __init__(self, key):
        self.key = key.encode('utf-8')[:16]
        self.iv = self.key
        self.mode = AES.MODE_CBC

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def encrypt(self, plaintext):
        # 加密
        cryptor = AES.new(self.key, self.mode, self.iv)
        plaintext = plaintext
        plaintext = self.pkcs7_padding(plaintext)
        ciphertext = cryptor.encrypt(plaintext)
        return b2a_hex(ciphertext).decode('utf-8')

    def decrypt(self, ciphertext):
        # 解密
        cryptor = AES.new(self.key, self.mode, self.iv)
        color_logger.info(f"decrypt解密方法获取参数ciphertext：{ciphertext}")
        plaintext = cryptor.decrypt(a2b_hex(ciphertext))
        color_logger.info(f"decrypt解密方法解析结果plaintext：{plaintext}")
        # https://blog.csdn.net/xc_zhou/article/details/126041906
        return bytes.decode(plaintext).rstrip("\x01").\
            rstrip("\x02").rstrip("\x03").rstrip("\x04").rstrip("\x05").\
            rstrip("\x06").rstrip("\x07").rstrip("\x08").rstrip("\x09").\
            rstrip("\x0a").rstrip("\x0b").rstrip("\x0c").rstrip("\x0d").\
            rstrip("\x0e").rstrip("\x0f").rstrip("\x10")
    
aes = AesCrypto(config_data['AES_KEY'])
