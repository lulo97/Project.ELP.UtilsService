def formatTranscriptRows(rows):
    """
    rows: Sqlite rows
    """
    if not rows:
        return None

    data = [
        {
            "text": row["text"],
            "start": row["start"],
            "end": row["end"]
        }
        for row in rows
    ]

    return data