import os
import sys

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


def pick_file_path_gui():
    """Open a system file dialog (no typing/paste needed). Uses tkinter (bundled on Windows)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return ""
    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    try:
        path = filedialog.askopenfilename(title="Select file to upload")
    finally:
        root.destroy()
    return path


def display_results(results):
    if not results:
        print("No matching files found.")
        return

    print("\nSearch Results:")
    print("----------------------")
    for i, file in enumerate(results, 1):
        try:
            print(f"{i}. {file}")
        except Exception:
            print(f"{i}. {file} (error reading file)")
    print("----------------------")


def prompt_read_decrypted_or_menu(results_list):
    """After matches are shown: decrypt & read one file, or return to the main menu."""
    if not results_list:
        return

    print()
    print("  [r]  Decrypt and read a file")
    print("  [m]  Back to main menu")
    choice = input("What next? (r/m): ").strip().lower()

    if choice in ("m", "menu", "b", "back"):
        return

    if choice not in ("r", "read", "d", "decrypt"):
        print("Unrecognized choice — returning to main menu.")
        return

    if len(results_list) == 1:
        filename = normalize_filename(results_list[0])
    else:
        filename = None
        while True:
            raw = input(f"Which file? Enter number 1–{len(results_list)}: ").strip()
            if not raw.isdigit():
                print("Enter a number from the list.")
                continue
            idx = int(raw)
            if 1 <= idx <= len(results_list):
                filename = normalize_filename(results_list[idx - 1])
                break
            print(f"Pick a number between 1 and {len(results_list)}.")

    try:
        data = load_file(filename)
    except FileNotFoundError:
        print(f"Encrypted copy not found for: {filename}")
        return
    except Exception as e:
        print(f"Could not decrypt: {e}")
        return

    print()
    print("─" * 56)
    print(f"Decrypted: {filename}")
    print("─" * 56)
    try:
        print(data.decode("utf-8"))
    except Exception:
        print(data.decode("utf-8", errors="replace"))
    print("─" * 56)


def _term(*seqs):
    """ANSI only when stdout is an interactive terminal."""
    if not sys.stdout.isatty():
        return ""
    return "".join(seqs)


def menu():
    """Draw the main menu (ANSI borders only so padding stays aligned)."""
    rs = _term("\033[0m")
    ac = _term("\033[38;5;109m")
    inner = 48
    bar = "─" * inner

    def row(body):
        # Plain text only inside the box so .ljust() matches terminal columns
        return f"  {ac}│{rs} {body.ljust(inner)} {ac}│{rs}"

    print()
    print(f"  {ac}╭{bar}╮{rs}")
    print(row("  ▸  SECURE SSE  ·  private keyword search"))
    print(row("     Encrypted files · local search index"))
    print(f"  {ac}├{bar}┤{rs}")
    for key, label in [
        ("1", "Upload file from computer"),
        ("2", "Create new file"),
        ("3", "Search files"),
        ("4", "Update file"),
        ("5", "Delete file"),
        ("6", "Exit"),
    ]:
        print(row(f"  {key}  ·  {label}"))
    print(f"  {ac}╰{bar}╯{rs}")
    print()


# -------------------------------
# Operations
# -------------------------------

def upload_file():
    import os

    print(
        "File path — paste the full path, or press Enter (or type b) to choose a file in a dialog."
    )
    print("  (In Windows Terminal: Ctrl+Shift+V to paste; in older CMD: right‑click → Paste.)")
    path = input("File path: ").strip()
    # Windows often pastes paths wrapped in quotes; that breaks os.path.exists
    path = path.strip('"').strip("'")

    if not path or path.lower() in ("b", "browse"):
        path = pick_file_path_gui()
        if not path:
            print("No file selected.")
            return

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
        print("File does not exist at that path.")
        print(
            "   Tip: Use the full path (no surrounding quotes). "
            "Bare filenames are only checked on Desktop and the app folder."
        )
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
                print("DOCX extraction failed:", e)
                print("File will NOT be indexed (to avoid garbage data)")
                text = ""

        else:
            print("Unsupported file type for keyword extraction")
            text = ""

        # -------------------------------
        # Step 3: VALIDATE TEXT (CRITICAL)
        # -------------------------------
        if not text.strip():
            print("No valid text extracted → skipping indexing")
            print(f"File still uploaded (encrypted): {filename}")
            return

        # 🔥 SAFETY CHECK (prevents your exact bug)
        if "Content_Types" in text:
            print("ERROR: Detected binary content — skipping indexing")
            return

        print("DEBUG TEXT PREVIEW:", text[:150])

        # -------------------------------
        # Step 4: Index clean text
        # -------------------------------
        add_document(filename, text)
        save()

        print(f"Uploaded and indexed: {filename}")

    except Exception as e:
        print(f"Upload failed: {e}")

def create_file():
    filename = input("Enter new file name: ").strip()
    filename = normalize_filename(filename)

    if not filename:
        print("Invalid filename.")
        return

    content = input("Enter file content:\n")

    try:
        save_file(filename, content.encode())
        add_document(filename, content)
        save()

        print(f"File created and indexed: {filename}")

    except Exception as e:
        print(f"Error creating file: {e}")


def search_files():
    query = input("Enter keyword(s): ").strip().lower()

    # 🔥 Split into multiple words
    words = query.split()

    if not words:
        print("Empty query")
        return

    try:
        all_results = []

        for word in words:
            results = search(word)
            all_results.append(set(results))

        # 🔥 INTERSECTION (files containing ALL words)
        final_results = set.intersection(*all_results) if all_results else set()

        results_list = sorted(final_results)
        display_results(results_list)
        prompt_read_decrypted_or_menu(results_list)

    except Exception as e:
        print(f"Search error: {e}")


def update_file():
    filename = input("Enter file name to update: ").strip()

    filepath = os.path.join("encrypted_files", filename + ".enc")

    # ✅ Proper existence check
    if not os.path.exists(filepath):
        print("No such file exists. Cannot update.")
        return

    new_content = input("Enter new content:\n")

    try:
        update_document(filename, new_content)
        save_file(filename, new_content.encode())
        save()

        print(f"File updated: {filename}")

    except Exception as e:
        print(f"Update failed: {e}")


def delete_file_cli():
    filename = input("Enter file name to delete: ").strip()
    filename = normalize_filename(filename)

    try:
        # Check existence
        load_file(filename)
    except:
        print("File does not exist.")
        return

    confirm = input(f"Are you sure you want to delete '{filename}'? (y/n): ")

    if confirm.lower() != "y":
        print("Deletion cancelled.")
        return

    try:
        delete_document(filename)
        delete_file(filename)
        save()

        print(f"File deleted: {filename}")

    except Exception as e:
        print(f"Delete failed: {e}")


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