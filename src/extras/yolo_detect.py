import os
import cv2
from ultralytics import YOLO

# ===============================
# CONFIG
# ===============================
FRAME_DIR = r"C:\Users\Ridhima\major-project\data\frames\uccrime_Robbery048_x264_5s"
OUT_DIR = r"C:\Users\Ridhima\major-project\outputs\bboxes_yolo\uccrime_Robbery048_x264_5s"
NUM_FRAMES = 10

os.makedirs(OUT_DIR, exist_ok=True)

# ===============================
# LOAD YOLOv8
# ===============================
model = YOLO("yolov8n.pt")  # nano = fast, enough for qualitative figs

frames = sorted([
    f for f in os.listdir(FRAME_DIR)
    if f.lower().endswith(".jpg")
])[:NUM_FRAMES]

for frame in frames:
    frame_path = os.path.join(FRAME_DIR, frame)
    image = cv2.imread(frame_path)

    results = model(image, conf=0.3, verbose=False)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image,
                label,
                (x1, max(15, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

    out_path = os.path.join(OUT_DIR, frame)
    cv2.imwrite(out_path, image)

    print(f"Saved YOLO bbox image → {out_path}")
