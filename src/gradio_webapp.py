# -------- SURVEILLANCE INTELLIGENCE ANALYZER DASHBOARD --------

import gradio as gr
import sqlite3
import pandas as pd
import os
import shutil
import logging
import traceback
from dotenv import load_dotenv
import google.generativeai as genai

# ---- Import working modules ----
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

        yield "Completed successfully.", base_video_name
        progress(1.0)

    except Exception as e:
        logger.error(traceback.format_exc())
        return f"Processing error: {str(e)}", None

# ---------------- Gemini Reasoning ----------------
def gemini_reasoning(context, question):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are a surveillance intelligence analyst.

Analyze the following chronological annotations.

Focus on suspicious behavior, risks, and key events.

If summary requested, structure:

1. Key Events
2. Potential Security Concerns
3. Overall Assessment

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
            return "Analyze a video first."

        conn = sqlite3.connect(DB_PATH)

        latest_ingest = pd.read_sql("""
            SELECT MAX(video_ingest_time) as latest
            FROM frame_annotations
            WHERE video_name = ?
        """, conn, params=(video_name,)).iloc[0]["latest"]

        if latest_ingest is None:
            conn.close()
            return "No annotations found."

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

# ---------------- Dashboard CSS ----------------
custom_css = """
/* Global */
body {
    background-color: #f4f6f8;
}

.gradio-container {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    color: #111827;
}

/* Header */
.header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-bottom: 18px;
    border-bottom: 4px solid #0f3d2e;
    margin-bottom: 30px;
}

.logo {
    font-size: 30px;
    font-weight: 700;
    color: #0f3d2e;
}

.app-title {
    font-size: 28px;
    font-weight: 800;
    color: #111827;
}

.app-subtitle {
    font-size: 14px;
    color: #4b5563;
    margin-top: 4px;
}

/* Card Sections */
.gr-group {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border: 1px solid #e5e7eb;
}

/* Section Titles */
h3 {
    font-weight: 700 !important;
    color: #111827 !important;
    margin-bottom: 16px !important;
}

/* Inputs */
textarea, input {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    padding: 10px !important;
    font-size: 14px !important;
}

/* Textbox output */
textarea[readonly] {
    background-color: #f9fafb !important;
}

/* Buttons */
button {
    background-color: #0f3d2e !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    border: none !important;
    transition: all 0.2s ease;
}

button:hover {
    background-color: #145c45 !important;
    transform: translateY(-1px);
}

/* Status Box */
label[for*="System Status"] + div textarea {
    font-weight: 500 !important;
}
"""


# ---------------- Dashboard Layout ----------------
with gr.Blocks(css=custom_css, title="Surveillance Intelligence Analyzer") as app:

    current_video_state = gr.State(None)
    # HTML header
    gr.HTML("""
        <div class="header">
            <div class="logo">🛡</div>
            <div>
                <div class="app-title">Surveillance Intelligence Analyzer</div>
                <div class="app-subtitle">
                    Frame-level video understanding with Florence-2 and intelligent reasoning powered by Gemini
                </div>
            </div>
        </div>
        """)


    # ----- Main Dashboard -----
    with gr.Row():

        # Left Column
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### Video Ingestion")
                video_upload = gr.File(file_types=[".mp4", ".avi", ".mov"])
                analyze_btn = gr.Button("Run Analysis")
                analyze_output = gr.Textbox(label="System Status")

                analyze_btn.click(
                    analyze_video,
                    inputs=video_upload,
                    outputs=[analyze_output, current_video_state],
                    show_progress=True
                )

        # Right Column
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("### Query & Intelligence")
                question = gr.Textbox(
                    label="Enter query",
                    placeholder="e.g., Identify suspicious activity",
                    lines=2
                )
                ask_btn = gr.Button("Generate Insight")
                answer_output = gr.Textbox(lines=20)

                ask_btn.click(
                    query_logs,
                    inputs=[question, current_video_state],
                    outputs=answer_output
                )

app.queue().launch()
