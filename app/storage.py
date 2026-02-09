import os
from .crypto import encrypt, decrypt

BASE = "encrypted_files"

os.makedirs(BASE, exist_ok=True)

def save_file(filename, data):
    blob = encrypt(data)
    with open(f"{BASE}/{filename}.enc", "wb") as f:
        f.write(blob)

def load_file(filename):
    with open(f"{BASE}/{filename}.enc", "rb") as f:
        return decrypt(f.read())

def delete_file(filename):
    path = f"{BASE}/{filename}.enc"
    if os.path.exists(path):
        os.remove(path)
