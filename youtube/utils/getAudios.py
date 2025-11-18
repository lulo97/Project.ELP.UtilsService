from utils.getConnection import getConnection

def getAudios():
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM video_audios")
    rows = cur.fetchall()
    if rows:
        return [row["video_id"] for row in rows]
    return []