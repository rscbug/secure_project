import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64


def get_hash(data: str)->str:
    return hashlib.md5(data.encode()).hexdigest()


def check_password_hash(pwhash: str, password: str) -> bool:
    return get_hash(password)==pwhash


def generate_password_hash(password: str) -> str:
    return get_hash(password)

def encrypt_data(key:str, iv:str, data:str) -> str:
    cipher = Cipher(algorithms.AES(str.encode(key)), modes.CBC(str.encode(iv)))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(str.encode(data)) + padder.finalize()
    ct = encryptor.update(padded_data) + encryptor.finalize()       
    base64.b64encode(ct).decode()
    return base64.b64encode(ct).decode()


def decrypt_data(key:str, iv:str, data:str)-> str:
    decoded_data = base64.b64decode(data)
    cipher = Cipher(algorithms.AES(str.encode(key)), modes.CBC(str.encode(iv)))
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(decoded_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plain_text=unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return plain_text.decode()