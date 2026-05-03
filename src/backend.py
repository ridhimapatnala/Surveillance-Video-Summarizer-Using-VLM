# -------- BACKEND: Processing, DB, Gemini --------

import sqlite3
import pandas as pd
import os
import shutil
import logging
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
import gradio as gr

from database import init_db, DB_PATH
from extract_frames_multivideo import extract_frames_every_n_seconds
from vlm_florence2 import process_video_frames

# ---------------- Logging ----------------
LOG_FILE = "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ---------------- Environment ----------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

VIDEO_DIR = r"C:\Users\Ridhima\major-project\data\videos"
FRAME_ROOT = r"C:\Users\Ridhima\major-project\data\frames"

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FRAME_ROOT, exist_ok=True)

init_db()

# ---------------- Analyze Pipeline ----------------
def analyze_video(file, progress=gr.Progress()):
    try:
        if file is None:
            return "Please upload a video.", None

        video_filename = os.path.basename(file.name)
        base_video_name = os.path.splitext(video_filename)[0]

        yield "Saving video...", None
        progress(0.2)

        save_path = os.path.join(VIDEO_DIR, video_filename)
        shutil.move(file.name, save_path)

        yield "Extracting frames...", None
        progress(0.4)

        extract_frames_every_n_seconds(
            video_path=save_path,
            output_root=FRAME_ROOT,
            seconds_per_frame=5
        )

        folder_name = f"{base_video_name}_5s"
        video_folder = os.path.join(FRAME_ROOT, folder_name)

        yield "Running Florence-2 analysis...", None
        progress(0.7)

        process_video_frames(video_folder)

        yield "Analysis complete.", base_video_name
        progress(1.0)

    except Exception as e:
        logger.error(traceback.format_exc())
        return f"Processing error: {str(e)}", None

# ---------------- Gemini Reasoning ----------------
def gemini_reasoning(context, question):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are a professional surveillance intelligence analyst.

        You are given chronological frame-level annotations extracted from a single video.

        CRITICAL RULES:
        - Use ONLY the provided annotations.
        - Do NOT assume events not explicitly described.
        - Do NOT double-count individuals across frames.
        - If asked about number of people, report the maximum number visible at one time (not a sum across frames).
        - Avoid redundancy.
        - Be precise and concise.
        - Keep responses under 150 words.
        - Be elaborate when asked to provide a summary or summarize key events.

        IF THE USER ASKS A QUESTION:
        - Answer directly using evidence from the annotations.
        - Do not speculate.
        - Provide a clear, factual response.

        IF THE USER REQUESTS A SUMMARY:
        Structure the response exactly as, and keep it to 200 words:

        1. Key Events  
        2. Potential Security Concerns  
        3. Overall Assessment  

        Each section should be brief and non-redundant.

        ANNOTATIONS:
        {context}

        QUESTION:
        {question}
        """
        response = model.generate_content(prompt)
        return response.text if response and response.text else "No response generated."

    except Exception as e:
        logger.error(traceback.format_exc())
        return f"Gemini error: {str(e)}"

# ---------------- Query DB ----------------
def query_logs(question, video_name):
    try:
        if video_name is None:
            return "No video analyzed yet. Upload and run analysis first."

        conn = sqlite3.connect(DB_PATH)

        latest_ingest = pd.read_sql("""
            SELECT MAX(video_ingest_time) as latest
            FROM frame_annotations
            WHERE video_name = ?
        """, conn, params=(video_name,)).iloc[0]["latest"]

        if latest_ingest is None:
            conn.close()
            return "No annotations found for this video."

        df = pd.read_sql("""
            SELECT frame_timestamp_sec, annotation
            FROM frame_annotations
            WHERE video_name = ?
            AND video_ingest_time = ?
            ORDER BY frame_timestamp_sec
        """, conn, params=(video_name, latest_ingest))

        conn.close()

        context = ""
        for _, row in df.iterrows():
            context += f"[{row['frame_timestamp_sec']} sec] {row['annotation']}\n"

        return gemini_reasoning(context, question)

    except Exception as e:
        logger.error(traceback.format_exc())
        return f"Database error: {str(e)}"