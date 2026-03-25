import json
import hmac
import hashlib
import re
from app.crypto import KEY  # ensure this works in your project

DOC_KEYWORDS_FILE = "data/doc_keywords.json"
INDEX_FILE = "data/index.json"

doc_keywords = {}
index = {}


# -------------------------------
# Normalize filename (CRITICAL)
# -------------------------------
def normalize_filename(name):
    name = name.strip()

    if name.endswith(".enc"):
        name = name[:-4]

    return name


# -------------------------------
# Tokenization (clean + consistent)
# -------------------------------
def tokenize(text):
    return re.findall(r"\w+", text.lower())


# -------------------------------
# Trapdoor (SECURE - HMAC)
# -------------------------------
def trapdoor(word):
    return hmac.new(KEY, word.encode(), hashlib.sha256).hexdigest()


# -------------------------------
# Add document
# -------------------------------
def add_document(filename, content):
    filename = normalize_filename(filename)

    words = set(tokenize(content))
    doc_keywords[filename] = list(words)

    for w in words:
        key = trapdoor(w)

        if key not in index:
            index[key] = []

        # Prevent duplicates
        if filename not in index[key]:
            index[key].append(filename)


# -------------------------------
# Save index
# -------------------------------
def save():
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    with open(DOC_KEYWORDS_FILE, "w") as f:
        json.dump(doc_keywords, f, indent=2)


# -------------------------------
# Load index
# -------------------------------
def load():
    global index, doc_keywords

    try:
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        index = {}

    try:
        with open(DOC_KEYWORDS_FILE, "r") as f:
            doc_keywords = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        doc_keywords = {}


# -------------------------------
# Search
# -------------------------------
def search(word):
    word = word.lower().strip()

    results = index.get(trapdoor(word), [])

    return list(set(results))  # remove duplicates


# -------------------------------
# Delete document
# -------------------------------
def delete_document(filename):
    filename = normalize_filename(filename)

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


# -------------------------------
# Update document
# -------------------------------
def update_document(filename, new_content):
    filename = normalize_filename(filename)

    delete_document(filename)
    add_document(filename, new_content)