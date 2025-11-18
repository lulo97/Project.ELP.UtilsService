def formatTimestamp(seconds):
    """Convert float seconds to HH:MM:SS.sss for yt-dlp."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:06.3f}"