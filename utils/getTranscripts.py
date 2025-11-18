from utils.getConnection import getConnection

def getTranscripts(video_id):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM video_transcripts WHERE video_id = ?", (video_id,))
    rows = cur.fetchall()
    return [dict(row) for row in rows]