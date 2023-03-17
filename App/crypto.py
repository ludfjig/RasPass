import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def encrypt(password, key):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(password.encode('utf-8'))
    # print("unpadded_data", padded_data, len(padded_data))
    padded_data += padder.finalize()
    # print("padded_data", padded_data, len(padded_data))

    iv = os.urandom(16)
    # print("iv", iv, len(iv))
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    cipher_text = iv + encryptor.update(padded_data) + encryptor.finalize()
    # print("ct", cipher_text, len(cipher_text))
    return base64.b64encode(cipher_text).decode('ascii')


def decrypt(cipher_text, key):

    # decryption
    cipher_text = base64.b64decode(cipher_text)
    iv = cipher_text[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plain_test = decryptor.update(
        cipher_text[16:]) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plain_text = unpadder.update(padded_plain_test)
    plain_text += unpadder.finalize()
    return str(plain_text, encoding='utf-8')
