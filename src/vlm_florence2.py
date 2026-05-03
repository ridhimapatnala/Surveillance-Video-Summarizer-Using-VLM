# -------- Florence-2 Windows flash_attn stub --------
import sys
import types
import importlib.machinery

flash_attn_stub = types.ModuleType("flash_attn")
flash_attn_stub.__spec__ = importlib.machinery.ModuleSpec(
    name="flash_attn",
    loader=None
)
sys.modules["flash_attn"] = flash_attn_stub
# ---------------------------------------------------

import os
import json
import sqlite3
import datetime
import torch
from PIL import Image
from tqdm import tqdm
from transformers import AutoConfig, AutoProcessor, AutoModelForCausalLM

from database import init_db, DB_PATH

DEVICE = torch.device("cpu")
MODEL_NAME = "kndrvitja/florence-SPHAR-finetune-2"
FRAME_ROOT = r"C:\Users\Ridhima\major-project\data\frames"
LOG_ROOT = r"C:\Users\Ridhima\major-project\logs"

os.makedirs(LOG_ROOT, exist_ok=True)

# Load model
config = AutoConfig.from_pretrained(MODEL_NAME, trust_remote_code=True)
if config.vision_config.model_type != "davit":
    config.vision_config.model_type = "davit"

processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    config=config,
    trust_remote_code=True
).to(DEVICE)

model.eval()

def annotate_frame(image_path: str, task="<SURVEILLANCE>"):
    image = Image.open(image_path).convert("RGB")

    if task == "<OD>":
        prompt = "<OD>"
    else:
        prompt = (
            "<SURVEILLANCE>"
            "Describe the key observable actions, interactions, or movements "
            "within this frame in 2–3 concise sentences."
        )

    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            num_beams=2,
            do_sample=False
        )

    return processor.batch_decode(outputs, skip_special_tokens=True)[0]

def parse_od_output(text):
    """
    Parses Florence-2 <OD> output into structured bounding boxes.
    """
    boxes = []

    text = text.replace("<OD>", "").strip()
    if not text:
        return boxes

    objects = text.split(";")

    for obj in objects:
        parts = obj.strip().split()
        if len(parts) != 5:
            continue

        label = parts[0]
        x1, y1, x2, y2 = map(float, parts[1:])

        boxes.append({
            "label": label,
            "bbox": (x1, y1, x2, y2)
        })

    return boxes


def process_video_frames(video_folder: str):
    folder_name = os.path.basename(video_folder)

    # Extract video name and sampling rate
    video_name, rate_part = folder_name.rsplit("_", 1)
    sampling_rate = int(rate_part.replace("s", ""))

    ingest_time = datetime.datetime.utcnow().isoformat()

    log_path = os.path.join(
        LOG_ROOT,
        f"{video_name}_{sampling_rate}s_annotations.jsonl"
    )

    with open(os.path.join(video_folder, "metadata.json")) as f:
        metadata = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(log_path, "w", encoding="utf-8") as log_file:
        for meta in tqdm(metadata, desc=f"{video_name} @ {sampling_rate}s"):
            frame_path = os.path.join(video_folder, meta["frame"])

            try:
                annotation = annotate_frame(frame_path)
            except Exception as e:
                annotation = f"ERROR: {str(e)}"

            record = {
                "video_name": video_name,
                "sampling_rate_seconds": sampling_rate,
                "frame": meta["frame"],
                "timestamp_sec": meta["timestamp_seconds"],
                "annotation": annotation
            }

            # Write per-video-per-rate log
            log_file.write(json.dumps(record) + "\n")

            # Insert into DB
            cursor.execute("""
                INSERT INTO frame_annotations (
                    video_name,
                    sampling_rate_seconds,
                    video_ingest_time,
                    frame_name,
                    frame_timestamp_sec,
                    frame_path,
                    annotation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                video_name,
                sampling_rate,
                ingest_time,
                meta["frame"],
                meta["timestamp_seconds"],
                frame_path,
                annotation
            ))

    conn.commit()
    conn.close()

    print(f"Completed {video_name} @ {sampling_rate}s")


if __name__ == "__main__":
    init_db()

    for folder in os.listdir(FRAME_ROOT):
        process_video_frames(os.path.join(FRAME_ROOT, folder))
