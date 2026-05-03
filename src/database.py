import sqlite3
import os

DB_PATH = "db/surveillance.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frame_annotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_name TEXT,
        sampling_rate_seconds INTEGER,
        video_ingest_time TEXT,
        frame_name TEXT,
        frame_timestamp_sec REAL,
        frame_path TEXT,
        annotation TEXT
    );

    """)

    conn.commit()
    conn.close()
