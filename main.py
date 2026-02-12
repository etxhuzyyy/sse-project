from app.storage import delete_file, save_file, load_file
from app.index import add_document, delete_document, save, load, search, update_document

load()

while True:
    cmd = input("upload/search/update/delete/exit: ")

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

    elif cmd == "update":
        name = input("filename: ")
        text = input("new content: ")
        update_document(name, text)
        save_file(name, text.encode())
        save()

    elif cmd == "delete":
        name = input("filename: ")
        delete_document(name)
        delete_file(name)
        save()

    else:
        break
