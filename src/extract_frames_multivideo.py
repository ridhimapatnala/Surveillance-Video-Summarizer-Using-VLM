import cv2
import os
import json

def extract_frames_every_n_seconds(
    video_path: str,
    output_root: str,
    seconds_per_frame: int
):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(
        output_root, f"{video_name}_{seconds_per_frame}s"
    )
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, int(fps * seconds_per_frame))

    frame_id = 0
    saved_id = 0
    metadata = []

    while frame_id < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_sec = round(frame_id / fps, 2)
        frame_name = f"frame_{saved_id:06d}.jpg"
        frame_path = os.path.join(output_dir, frame_name)

        cv2.imwrite(frame_path, frame)

        metadata.append({
            "frame": frame_name,
            "timestamp_seconds": timestamp_sec,
            "source_frame_id": frame_id,
            "sampling_rate_seconds": seconds_per_frame
        })

        saved_id += 1
        frame_id += frame_interval

    cap.release()

    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(
        f"[{video_name} | {seconds_per_frame}s] "
        f"Extracted {saved_id} frames"
    )


if __name__ == "__main__":

    VIDEO_DIR = r"C:\Users\Ridhima\major-project\data\videos"
    OUTPUT_ROOT = r"C:\Users\Ridhima\major-project\data\frames"

    # 🔑 MULTIRATE SETTINGS
    SAMPLING_RATES = [1, 2, 5, 10]

    for video_file in os.listdir(VIDEO_DIR):
        if not video_file.lower().endswith((".mp4", ".avi", ".mov")):
            continue

        video_path = os.path.join(VIDEO_DIR, video_file)

        for rate in SAMPLING_RATES:
            extract_frames_every_n_seconds(
                video_path=video_path,
                output_root=OUTPUT_ROOT,
                seconds_per_frame=rate
            )
