import os
import platform
import subprocess
import sqlite3
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.getConnection import getConnection
from utils.getRandomId import getRandomId

parent_folder = os.path.dirname(os.path.abspath(__file__))

def fetchAudio(video_id):
    """
    Fetch audio from YouTube via yt-dlp, and store file path in db.
    """
    conn = getConnection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
        
    cur.execute("""
        SELECT * FROM video_audios
        WHERE video_id = ?
    """, (video_id,))

    row = cur.fetchone()

    if row:
        print(f"[CACHE] Audio found for {video_id}")
        return {"format": "mp3", "file_name": row["file_name"]}

    # Pick yt-dlp path based on OS
    if platform.system() == "Windows":
        yt_dlp_path = os.path.join(parent_folder, "windows", "yt-dlp.exe")
    else:
        yt_dlp_path = os.path.join(parent_folder, "linux", "yt-dlp")
        
    command = [
        yt_dlp_path,
        "--quiet", "--no-warnings",
        "-x", "--audio-format", "mp3",
        "-o", "%(id)s.%(ext)s",
        "--audio-quality", "64K",
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    print(f"[DOWNLOAD] Running yt-dlp from {yt_dlp_path} for {video_id}")

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError(f"yt-dlp executable not found at: {yt_dlp_path}")
    except subprocess.CalledProcessError as e:
        print("[ERROR] yt-dlp failed:", e.stderr.decode("utf-8", errors="ignore"))
        raise RuntimeError("Failed to download audio from YouTube")

    downloaded_file = f"{video_id}.mp3"
    if not os.path.exists(downloaded_file):
        raise FileNotFoundError(f"Expected file '{downloaded_file}' not found")

    # Move to storage folder
    safe_video_id = video_id.replace("/", "_").replace("\\", "_")
    file_name = f"{safe_video_id}.mp3"
    dest_folder = "./database/audios"
    os.makedirs(dest_folder, exist_ok=True)
    shutil.move(downloaded_file, os.path.join(dest_folder, file_name))  # ✅ shutil.move

    # Insert into DB
    cur.execute("""
        INSERT INTO video_audios (id, video_id, file_name)
        VALUES (?, ?, ?)
    """, (getRandomId(), video_id, file_name))
    
    conn.commit()

    print(f"[INSERTED] Cached audio for {video_id}")

    return {"file_name": file_name, "format": "mp3"}
