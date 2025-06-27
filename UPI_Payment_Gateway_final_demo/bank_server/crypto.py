
import hashlib
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Tuple

def generate_sha256_hash(input_str: str) -> str:
    
    hash_object = hashlib.sha256(input_str.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig[:16]  

def encrypt_data(data: str, key: bytes = None) -> Tuple[bytes, bytes]:
    
    if key is None:
        key = os.urandom(32)  
    iv = os.urandom(12)  
    
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()
    return encrypted_data, iv, key, encryptor.tag

def decrypt_data(encrypted_data: bytes, iv: bytes, key: bytes, tag: bytes) -> str:
    
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data.decode()
