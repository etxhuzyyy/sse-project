import json
import hmac
import hashlib
import re
from app.crypto import KEY  # if this gives import error, try: from crypto import KEY

DOC_KEYWORDS_FILE = "data/doc_keywords.json"
INDEX_FILE = "data/index.json"

doc_keywords = {}
index = {}

def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())

def trapdoor(word):
    return hmac.new(KEY, word.encode(), hashlib.sha256).hexdigest()

def add_document(filename, content):
    words = set(tokenize(content))
    doc_keywords[filename] = list(words)

    for w in words:
        key = trapdoor(w)
        if filename not in index.setdefault(key, []):
            index[key].append(filename)

def save():
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    with open(DOC_KEYWORDS_FILE, "w") as f:
        json.dump(doc_keywords, f, indent=2)

def load():
    global index, doc_keywords

    try:
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
    except FileNotFoundError:
        index = {}
    except json.JSONDecodeError:
        index = {}

    try:
        with open(DOC_KEYWORDS_FILE, "r") as f:
            doc_keywords = json.load(f)
    except FileNotFoundError:
        doc_keywords = {}
    except json.JSONDecodeError:
        doc_keywords = {}

def search(word):
    return index.get(trapdoor(word), [])

def delete_document(filename):
    if filename not in doc_keywords:
        return

    words = doc_keywords[filename]

    for w in words:
        key = trapdoor(w)
        if key in index and filename in index[key]:
            index[key].remove(filename)
            if not index[key]:
                del index[key]

    del doc_keywords[filename]

def update_document(filename, new_content):
    delete_document(filename)
    add_document(filename, new_content)