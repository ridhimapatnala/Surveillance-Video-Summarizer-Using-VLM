import cv2
import os

def extract_frames(video_path, output_dir, fps=1):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(video_fps // fps)

    frame_id = 0
    saved_id = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % interval == 0:
            frame_name = f"frame_{saved_id:06d}.jpg"
            cv2.imwrite(os.path.join(output_dir, frame_name), frame)
            saved_id += 1

        frame_id += 1

    cap.release()
    print(f"Extracted {saved_id} frames")

if __name__ == "__main__":
    extract_frames(
        video_path="data/videos/Burglary002_x264A.mp4",
        output_dir="data/frames",
        fps=1
    )
