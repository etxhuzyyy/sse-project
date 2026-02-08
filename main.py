from app.storage import save_file, load_file
from app.index import add_document, save, load, search

load()

while True:
    cmd = input("upload/search/exit: ")

    if cmd == "upload":
        name = input("filename: ")
        text = input("content: ")

        save_file(name, text.encode())
        add_document(name, text)
        save()

    elif cmd == "search":
        word = input("keyword: ")
        results = search(word)

        for r in results:
            print(r, load_file(r).decode())

    else:
        break
