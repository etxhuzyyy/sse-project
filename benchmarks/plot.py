import json
import matplotlib.pyplot as plt


# ---------------- Search Latency Plot ----------------
def plot_search_latency():
    with open("benchmarks/search_results.json") as f:
        data = json.load(f)

    x = sorted(int(k) for k in data.keys())
    y = [data[str(k)]["search_time_sec"] for k in x]

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.xlabel("Number of Files")
    plt.ylabel("Search Latency (seconds)")
    plt.title("SSE Search Latency")
    plt.grid(True)
    plt.show()


# ---------------- Index Size Growth Plot ----------------
def plot_index_growth():
    with open("benchmarks/index_growth.json") as f:
        data = json.load(f)

    x = sorted(int(k) for k in data.keys())
    y = [data[str(k)] for k in x]

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.xlabel("Number of Files")
    plt.ylabel("Index Size (KB)")
    plt.title("SSE Index Size Growth")
    plt.grid(True)
    plt.show()


# ---------------- Update Time Plot ----------------
def plot_update_time():
    with open("benchmarks/update_results.json") as f:
        data = json.load(f)

    x = sorted(int(k) for k in data.keys())
    y = [data[str(k)] for k in x]

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.xlabel("Number of Files")
    plt.ylabel("Update Time (seconds)")
    plt.title("SSE Update Time (Dynamic SSE)")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    plot_search_latency()
    plot_index_growth()
    plot_update_time()
