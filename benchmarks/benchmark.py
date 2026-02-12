import time
import random
import os
import json

from app.index import add_document, search, save
from app.storage import save_file
from app import index as index_module


# ---------------- Synthetic Data ----------------
def random_text(words=20):
    vocab = [
        "network", "security", "privacy", "encryption",
        "cloud", "searchable", "symmetric", "data"
    ]
    return " ".join(random.choice(vocab) for _ in range(words))


# ---------------- Reset Environment ----------------
def reset_environment():
    # Clear in-memory structures
    index_module.index = {}
    index_module.doc_keywords = {}

    # Remove index files
    if os.path.exists("data/index.json"):
        os.remove("data/index.json")

    if os.path.exists("data/doc_keywords.json"):
        os.remove("data/doc_keywords.json")

    # Remove encrypted files
    if os.path.exists("encrypted_files"):
        for f in os.listdir("encrypted_files"):
            os.remove(os.path.join("encrypted_files", f))


# ---------------- Search Latency Benchmark ----------------
def average_search_time(keyword="security", trials=5):
    total = 0
    for _ in range(trials):
        start = time.time()
        search(keyword)
        end = time.time()
        total += (end - start)
    return total / trials


def benchmark_search_latency(sizes):
    results = {}

    print("\nSSE Benchmark (Search Latency)")
    print("--------------------------------")

    for s in sizes:
        reset_environment()

        # Generate dataset
        for i in range(s):
            content = random_text()
            name = f"file{i}"
            save_file(name, content.encode())
            add_document(name, content)

        save()

        latency = average_search_time()
        index_kb = measure_index_size()

        results[s] = {
            "search_time_sec": latency,
            "index_size_kb": index_kb
        }

        print(f"{s:>5} files | search: {latency:.6f}s | index: {index_kb:.2f} KB")

    return results


# ---------------- Index Size Measurement ----------------
def measure_index_size():
    if os.path.exists("data/index.json"):
        return os.path.getsize("data/index.json") / 1024  # KB
    return 0


def benchmark_index_growth(sizes):
    results = {}

    print("\nSSE Benchmark (Index Size Growth)")
    print("-----------------------------------")

    for s in sizes:
        reset_environment()

        for i in range(s):
            content = random_text()
            name = f"file{i}"
            save_file(name, content.encode())
            add_document(name, content)

        save()

        size_kb = measure_index_size()
        results[s] = size_kb

        print(f"{s:>5} files | index size: {size_kb:.2f} KB")

    return results


# ---------------- Update Time Benchmark ----------------
def benchmark_update_time(sizes):
    from app.index import update_document

    results = {}

    print("\nSSE Benchmark (Update Time)")
    print("--------------------------------")

    for s in sizes:
        reset_environment()

        # Generate dataset
        for i in range(s):
            content = random_text()
            name = f"file{i}"
            save_file(name, content.encode())
            add_document(name, content)

        save()

        # Measure update
        start = time.time()
        update_document("file0", random_text())
        save()
        end = time.time()

        update_time = end - start
        results[s] = update_time

        print(f"{s:>5} files | update time: {update_time:.6f}s")

    return results


# ---------------- Run All Benchmarks ----------------
def run_all():
    sizes = [100, 500, 1000, 2000]

    os.makedirs("benchmarks", exist_ok=True)

    search_results = benchmark_search_latency(sizes)
    index_results = benchmark_index_growth(sizes)
    update_results = benchmark_update_time(sizes)

    # Save all results
    with open("benchmarks/search_results.json", "w") as f:
        json.dump(search_results, f, indent=2)

    with open("benchmarks/index_growth.json", "w") as f:
        json.dump(index_results, f, indent=2)

    with open("benchmarks/update_results.json", "w") as f:
        json.dump(update_results, f, indent=2)

    print("\nAll benchmarks completed and saved.")


if __name__ == "__main__":
    run_all()
