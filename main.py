import os
from app.storage import delete_file, save_file, load_file
from app.index import add_document, delete_document, save, load, search, update_document

# Load index at startup
load()


# -------------------------------
# Helper Functions
# -------------------------------

def display_results(results):
    if not results:
        print("🔍 No matching files found.")
        return

    print("\n🔍 Search Results:")
    print("----------------------")
    for i, file in enumerate(results, 1):
        try:
            content = load_file(file).decode(errors="ignore")
            print(f"{i}. {file} → {content[:50]}...")
        except:
            print(f"{i}. {file} (error reading file)")
    print("----------------------")


# -------------------------------
# Operations
# -------------------------------

def upload_file():
    path = input("Enter file path: ").strip()

    if not os.path.exists(path):
        print("❌ File does not exist.")
        return

    filename = os.path.basename(path)

    try:
        with open(path, "rb") as f:
            content = f.read()

        save_file(filename, content)
        add_document(filename, content.decode(errors="ignore"))
        save()

        print(f"✅ Uploaded and indexed: {filename}")

    except Exception as e:
        print(f"⚠️ Upload failed: {e}")


def create_file():
    filename = input("Enter new file name: ").strip()

    if not filename:
        print("❌ Invalid filename.")
        return

    content = input("Enter file content:\n")

    try:
        save_file(filename, content.encode())
        add_document(filename, content)
        save()

        print(f"✅ File created and indexed: {filename}")

    except Exception as e:
        print(f"⚠️ Error creating file: {e}")


def search_files():
    keyword = input("Enter keyword: ").strip()

    try:
        results = search(keyword)
        display_results(results)

    except Exception as e:
        print(f"⚠️ Search error: {e}")


def update_file():
    filename = input("Enter file name to update: ").strip()

    filepath = os.path.join("encrypted_files", filename)

    # ✅ Proper existence check
    if not os.path.exists(filepath):
        print("❌ No such file exists. Cannot update.")
        return

    new_content = input("Enter new content:\n")

    try:
        update_document(filename, new_content)
        save_file(filename, new_content.encode())
        save()

        print(f"✅ File updated: {filename}")

    except Exception as e:
        print(f"⚠️ Update failed: {e}")
    filename = input("Enter file name to update: ").strip()

    try:
        # Check if file exists
        load_file(filename)
    except:
        print("❌ File does not exist. Cannot update.")
        return

    new_content = input("Enter new content:\n")

    try:
        update_document(filename, new_content)
        save_file(filename, new_content.encode())
        save()

        print(f"✅ File updated: {filename}")

    except Exception as e:
        print(f"⚠️ Update failed: {e}")


def delete_file_cli():
    filename = input("Enter file name to delete: ").strip()

    try:
        # Check existence
        load_file(filename)
    except:
        print("❌ File does not exist.")
        return

    confirm = input(f"Are you sure you want to delete '{filename}'? (y/n): ")

    if confirm.lower() != "y":
        print("❌ Deletion cancelled.")
        return

    try:
        delete_document(filename)
        delete_file(filename)
        save()

        print(f"🗑️ File deleted: {filename}")

    except Exception as e:
        print(f"⚠️ Delete failed: {e}")


# -------------------------------
# Main Menu
# -------------------------------

def menu():
    print("\n==== Secure SSE File System ====")
    print("1. Upload file from computer")
    print("2. Create new file")
    print("3. Search files")
    print("4. Update file")
    print("5. Delete file")
    print("6. Exit")


# -------------------------------
# Main Loop
# -------------------------------

while True:
    try:
        menu()
        choice = input("Select option: ").strip()

        if choice == "1":
            upload_file()

        elif choice == "2":
            create_file()

        elif choice == "3":
            search_files()

        elif choice == "4":
            update_file()

        elif choice == "5":
            delete_file_cli()

        elif choice == "6":
            print("👋 Exiting...")
            break

        else:
            print("❌ Invalid choice")

    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")