import json
import hashlib

DOC_KEYWORDS_FILE = "data/doc_keywords.json"
doc_keywords = {}

INDEX_FILE = "data/index.json"

index = {}

def tokenize(text):
    return text.lower().split()

def trapdoor(word):
    return hashlib.sha256(word.encode()).hexdigest()

def add_document(filename, content):
    words = set(tokenize(content))
    doc_keywords[filename] = list(words)

    for w in words:
        key = trapdoor(w)
        index.setdefault(key, []).append(filename)


def save():
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f)
    with open(DOC_KEYWORDS_FILE, "w") as f:
        json.dump(doc_keywords, f)

def load():
    global index, doc_keywords
    try:
        with open(INDEX_FILE) as f:
            index = json.load(f)
        with open(DOC_KEYWORDS_FILE) as f:
            doc_keywords = json.load(f)
    except:
        index = {}
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
