from Crypto.Cipher import DES3
from base64 import b64decode
from binascii import a2b_hex, b2a_hex
from pyDes import des, CBC, PAD_PKCS5


def get_pwd(plaintext):
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    secret_key = '%$#(*N@M'
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(a2b_hex(plaintext), padmode=PAD_PKCS5).decode()
    return de


def get_pwd_old_version(plaintext):
    key = b'%$#(*N@MHGPL><NRMvMghsO*'
    cipher = DES3.new(key, DES3.MODE_ECB)
    plaintext = b64decode(bytes(plaintext, encoding='utf-8'))
    pwd = cipher.decrypt(plaintext).decode('utf-8')
    # msg = cipher.encrypt(mk)
    return pwd

def get_pwd_encryped(plaintext):
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = '%$#(*N@M'
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(plaintext, padmode=PAD_PKCS5)
    return b2a_hex(en)



# print(get_pwd('57b383d0b39d8d647dfc8979313f4ec1'))