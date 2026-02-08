import json
import hashlib

INDEX_FILE = "data/index.json"

index = {}

def tokenize(text):
    return text.lower().split()

def trapdoor(word):
    return hashlib.sha256(word.encode()).hexdigest()

def add_document(filename, content):
    words = set(tokenize(content))
    for w in words:
        key = trapdoor(w)
        index.setdefault(key, []).append(filename)

def save():
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f)

def load():
    global index
    try:
        with open(INDEX_FILE) as f:
            index = json.load(f)
    except:
        index = {}

def search(word):
    return index.get(trapdoor(word), [])
