import os
import json
import re
import matplotlib.pyplot as plt

LOG_DIR = r"C:\Users\Ridhima\major-project\logs"
SIMILARITY_THRESHOLD = 0.6  # Jaccard similarity

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return set(text.split())

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def load_annotations_by_rate(log_dir):
    data = {}

    for file in os.listdir(log_dir):
        if not file.endswith(".jsonl"):
            continue

        # video1_5s_annotations.jsonl
        rate = int(file.split("_")[-2].replace("s", ""))

        with open(os.path.join(log_dir, file), "r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                data.setdefault(rate, []).append(rec["annotation"])

    return data

def count_unique_semantics(sentences):
    normalized = [normalize(s) for s in sentences]
    used = set()
    unique = 0

    for i in range(len(normalized)):
        if i in used:
            continue
        unique += 1
        for j in range(i + 1, len(normalized)):
            if jaccard(normalized[i], normalized[j]) >= SIMILARITY_THRESHOLD:
                used.add(j)

    return unique

def main():
    data = load_annotations_by_rate(LOG_DIR)

    rates = sorted(data.keys())
    total_frames = []
    efficiency = []
    redundancy = []

    for rate in rates:
        annotations = data[rate]
        n_frames = len(annotations)
        n_unique = count_unique_semantics(annotations)

        eff = n_unique / n_frames
        red = 1 - eff

        total_frames.append(n_frames)
        efficiency.append(eff)
        redundancy.append(red)

        print(
            f"{rate}s → frames={n_frames}, "
            f"unique={n_unique}, "
            f"efficiency={eff:.3f}, "
            f"redundancy={red:.3f}"
        )

    # ------------------- PROFESSIONAL PLOT -------------------
    plt.figure(figsize=(6, 4))

    plt.plot(
        total_frames,
        efficiency,
        marker="o",
        linestyle="-",
        linewidth=1.8,
        markersize=6,
        color="black",
        label="Efficiency"
    )

    plt.plot(
        total_frames,
        redundancy,
        marker="s",
        linestyle="--",
        linewidth=1.8,
        markersize=6,
        color="gray",
        label="Redundancy"
    )

    plt.xlabel("Number of Frames", fontsize=11)
    plt.ylabel("Score", fontsize=11)

    plt.title(
        "Efficiency and Redundancy vs Frame Count",
        fontsize=12,
        pad=8
    )

    plt.legend(frameon=False, fontsize=10)

    plt.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.4
    )

    plt.tight_layout()

    # Save for paper & slides
    plt.savefig("efficiency_redundancy_plot.pdf", dpi=300)
    plt.savefig("efficiency_redundancy_plot.png", dpi=300)

    plt.show()
if __name__ == "__main__":
    main()
