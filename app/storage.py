import os
from .crypto import encrypt, decrypt

BASE = "encrypted_files"

os.makedirs(BASE, exist_ok=True)


# -------------------------------
# Normalize filename (CRITICAL)
# -------------------------------
def normalize_filename(filename):
    filename = filename.strip()

    # Remove .enc if user or code passes it
    if filename.endswith(".enc"):
        filename = filename[:-4]

    return filename


# -------------------------------
# Save File (Encrypted)
# -------------------------------
def save_file(filename, data):
    filename = normalize_filename(filename)

    path = os.path.join(BASE, filename + ".enc")

    blob = encrypt(data)

    with open(path, "wb") as f:
        f.write(blob)


# -------------------------------
# Load File (Decrypt)
# -------------------------------
def load_file(filename):
    filename = normalize_filename(filename)

    path = os.path.join(BASE, filename + ".enc")

    if not os.path.exists(path):
        raise FileNotFoundError("File does not exist")

    with open(path, "rb") as f:
        return decrypt(f.read())


# -------------------------------
# Delete File
# -------------------------------
def delete_file(filename):
    filename = normalize_filename(filename)

    path = os.path.join(BASE, filename + ".enc")

    if os.path.exists(path):
        os.remove(path)