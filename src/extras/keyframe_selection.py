import os
import random
import matplotlib.pyplot as plt
import json

def select_keyframes(frame_dir, k):
    frames = sorted(os.listdir(frame_dir))
    return random.sample(frames, min(k, len(frames)))

def evaluate_coverage(selected_frames, logs):
    detected = set()
    for row in logs:
        if row["frame"] in selected_frames:
            detected.add(row["annotation"])
    return len(detected)

def load_logs(path):
    with open(path) as f:
        return [json.loads(l) for l in f]

def plot_keyframe_efficiency(frame_dir, log_path):
    logs = load_logs(log_path)
    ks = [5, 10, 20, 40, 80]
    coverage_scores = []

    for k in ks:
        selected = select_keyframes(frame_dir, k)
        coverage = evaluate_coverage(selected, logs)
        coverage_scores.append(coverage)

    plt.plot(ks, coverage_scores, marker="o")
    plt.xlabel("Number of keyframes")
    plt.ylabel("Semantic coverage")
    plt.title("Keyframe Efficiency Curve")
    plt.savefig("plots/keyframe_efficiency.png")
    plt.show()

if __name__ == "__main__":
    plot_keyframe_efficiency(
        frame_dir="data/frames",
        log_path="logs/frame_logs.jsonl"
    )
