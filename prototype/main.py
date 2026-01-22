import subprocess
import os
from pathlib import Path

# =========================
# CONFIG
# =========================

YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
OUTPUT_DIR = Path("outputs")
VIDEO_PATH = OUTPUT_DIR / "input.mp4"

# =========================
# UTILS
# =========================

def run_command(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

# =========================
# MAIN
# =========================

def download_youtube_video():
    OUTPUT_DIR.mkdir(exist_ok=True)

    cmd = [
    "yt-dlp",
    "-f", "bv*+ba/b",
    "--merge-output-format", "mp4",
    "--cookies-from-browser", "chrome",
    "-o", str(VIDEO_PATH),
    YOUTUBE_URL
]


    run_command(cmd)

    if not VIDEO_PATH.exists():
        raise RuntimeError("Video download failed")

    print(f"Downloaded video to {VIDEO_PATH}")



def get_video_duration():
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(VIDEO_PATH)
    ]

    result = subprocess.check_output(cmd).decode().strip()
    duration = float(result)
    print(f"Video duration: {duration:.2f} seconds")
    return duration

def main():
    download_youtube_video()
    get_video_duration()

if __name__ == "__main__":
    main()
