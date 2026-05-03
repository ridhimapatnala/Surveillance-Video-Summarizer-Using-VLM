# -------- ENTRY POINT --------
# python src/app.py
from backend import analyze_video, query_logs
from ui import build_ui

app = build_ui(
    analyze_video_fn=analyze_video,
    query_logs_fn=query_logs
)

app.queue().launch()