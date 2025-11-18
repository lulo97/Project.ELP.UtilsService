import os
from youtube_transcript_api import YouTubeTranscriptApi
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.formatTranscriptRows import formatTranscriptRows
from utils.getConnection import getConnection
from utils.getRandomId import getRandomId

parent_folder = os.path.dirname(os.path.abspath(__file__))

def fetchTranscript(video_id):
    """
    Fetch transcript from YouTube video.
    If already in DB, read from DB; otherwise, fetch and store.
    """
    conn = getConnection()
    cur = conn.cursor()

    cur.execute("SELECT text, start, end FROM video_transcripts WHERE video_id = ?", (video_id,))
    rows = cur.fetchall()
    if rows:
        print(f"[CACHE] Transcript found for {video_id}")
        return formatTranscriptRows(rows)

    print(f"[FETCH] Fetching transcript for {video_id}")
    
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.fetch(video_id)

    for t in transcript_list.snippets:
        cur.execute("""
            INSERT INTO video_transcripts (id, video_id, start, end, text)
            VALUES (?, ?, ?, ?, ?)
        """, (
            getRandomId(),
            transcript_list.video_id,
            t.start,
            t.start + t.duration,
            t.text
        ))
    
    conn.commit()
    
    cur.execute("SELECT text, start, end FROM video_transcripts WHERE video_id = ?", (video_id,))
    
    rows = cur.fetchall()
    
    if rows:
        return formatTranscriptRows(rows)
