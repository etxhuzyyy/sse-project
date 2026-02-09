import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

KEY_FILE = "data/secret.key"

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = get_random_bytes(16)
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

KEY = load_key()

def encrypt(data: bytes):
    cipher = AES.new(KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext

def decrypt(blob: bytes):
    nonce = blob[:16]
    tag = blob[16:32]
    ciphertext = blob[32:]

    cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)