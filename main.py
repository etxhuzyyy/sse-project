import os

from matplotlib import text
from app.storage import delete_file, save_file, load_file
from app.index import add_document, delete_document, save, load, search, update_document

# Load index at startup
load()


# -------------------------------
# Helper Functions
# -------------------------------

def normalize_filename(name):
    name = name.strip()

    # remove .enc if user typed it
    if name.endswith(".enc"):
        name = name[:-4]

    return name

def display_results(results):
    if not results:
        print("🔍 No matching files found.")
        return

    print("\n🔍 Search Results:")
    print("----------------------")
    for i, file in enumerate(results, 1):
        try:
            print(f"{i}. {file}")
        except:
            print(f"{i}. {file} (error reading file)")
    print("----------------------")


# -------------------------------
# Operations
# -------------------------------

def upload_file():
    import os

    path = input("Enter file path: ").strip()

    # ✅ Expand ~ (home directory)
    path = os.path.expanduser(path)

    # ✅ If user enters just filename → assume Desktop
    if not os.path.isabs(path):
        desktop_path = os.path.join(os.path.expanduser("~/Desktop"), path)
        if os.path.exists(desktop_path):
            path = desktop_path

    # ✅ Normalize path (handles weird slashes, spaces, etc.)
    path = os.path.normpath(path)

    print("DEBUG PATH:", path)  # optional but useful

    if not os.path.exists(path):
        print("❌ File does not exist.")
        return

    filename = os.path.basename(path)
    filename = normalize_filename(filename)

    try:
        # -------------------------------
        # Step 1: Read file for encryption
        # -------------------------------
        with open(path, "rb") as f:
            content = f.read()

        # Save encrypted file
        save_file(filename, content)

        # -------------------------------
        # Step 2: Extract TEXT for indexing
        # -------------------------------
        text = ""

        if filename.lower().endswith(".txt"):
            try:
                text = content.decode("utf-8")
            except:
                text = content.decode(errors="ignore")

        elif filename.lower().endswith(".docx"):
            try:
                from docx import Document

                doc = Document(path)

                text_parts = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text.strip())

                text = " ".join(text_parts)

                print("✅ DOCX text extracted successfully")

            except Exception as e:
                print("❌ DOCX extraction failed:", e)
                print("⚠️ File will NOT be indexed (to avoid garbage data)")
                text = ""

        else:
            print("⚠️ Unsupported file type for keyword extraction")
            text = ""

        # -------------------------------
        # Step 3: VALIDATE TEXT (CRITICAL)
        # -------------------------------
        if not text.strip():
            print("⚠️ No valid text extracted → skipping indexing")
            print(f"✅ File still uploaded (encrypted): {filename}")
            return

        # 🔥 SAFETY CHECK (prevents your exact bug)
        if "Content_Types" in text:
            print("❌ ERROR: Detected binary content — skipping indexing")
            return

        print("DEBUG TEXT PREVIEW:", text[:150])

        # -------------------------------
        # Step 4: Index clean text
        # -------------------------------
        add_document(filename, text)
        save()

        print(f"✅ Uploaded and indexed: {filename}")

    except Exception as e:
        print(f"⚠️ Upload failed: {e}")

def create_file():
    filename = input("Enter new file name: ").strip()
    filename = normalize_filename(filename)

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
    query = input("Enter keyword(s): ").strip().lower()

    # 🔥 Split into multiple words
    words = query.split()

    if not words:
        print("❌ Empty query")
        return

    try:
        all_results = []

        for word in words:
            results = search(word)
            all_results.append(set(results))

        # 🔥 INTERSECTION (files containing ALL words)
        final_results = set.intersection(*all_results) if all_results else set()

        display_results(list(final_results))

    except Exception as e:
        print(f"⚠️ Search error: {e}")
    keyword = input("Enter keyword: ").strip()

    try:
        results = search(keyword)
        display_results(results)

    except Exception as e:
        print(f"⚠️ Search error: {e}")


def update_file():
    filename = input("Enter file name to update: ").strip()

    filepath = os.path.join("encrypted_files", filename + ".enc")

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
    filename = normalize_filename(filename)

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