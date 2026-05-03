# Surveillance Video Summarization System Using VLMs

## Overview

This project processes surveillance videos and generates meaningful summaries from them. Instead of manually watching long footage, the system extracts key frames, analyzes them using AI models, and produces a concise description of important events.

---

## Features

* Upload and process surveillance videos
* Extract key frames efficiently
* Analyze frames using vision-language models
* Generate textual summaries of events
* Simple web interface using Gradio

---

## Project Structure

```
major-project/
│── src/
│   ├── app.py                  # Main entry point
│   ├── backend.py              # Core processing logic
│   ├── database.py             # DB handling
│   ├── extract_frames_multivideo.py
│   ├── gradio_webapp.py        # UI
│   ├── ui.py
│   ├── vlm_florence2.py        # Vision-language model logic
│   └── extras/
│
│── data/                       # Input videos
│── outputs/                    # Generated results
│── logs/                       # Logs
│── db/                         # Database files
│── plots/                      # Visual outputs
│
│── requirements.txt
│── README.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

### 2. Create and activate virtual environment

```bash
python -m venv venv
```


---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set up environment variables

Create a `.env` file in the root directory and add:

```env
GEMINI_API_KEY=your_api_key_here
```

Make sure this key is valid, otherwise the model won’t work.

---


### 5. Run the main application:

```bash
python src/app.py
```

After running, you’ll see a local URL(usually). Open in your browser to use the app.

---

## How It Works

1. User uploads a surveillance video
2. Video is split into frames using OpenCV
3. Key frames are selected to reduce computation
4. Frames are analyzed using AI models (Gemini / VLM)
5. A final summary is generated

---

## Notes

* Ensure your **GEMINI API KEY** is set before running
* Large videos may take time depending on system performance
* Outputs are saved in the `outputs/` folder

---

## Future Improvements

* Real-time video processing
* Better event detection models
* Cloud deployment support

---
