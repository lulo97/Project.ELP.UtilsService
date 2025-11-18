import os
from bottle import Bottle, run, request, response, abort
import json
from utils.getConfig import getConfig
from youtube.utils.fetchAudio import fetchAudio
from youtube.utils.fetchTranscript import fetchTranscript
from text_to_speech.textToSpeech import textToSpeech
from speech_to_text.speechToText import speechToText

app = Bottle()


@app.post("/stt")
def stt():
    base64 = request.body.get("base64")
    result = speechToText(base64_audio=base64)
    response.content_type = "application/json"
    return json.dumps({"error": None, "data": {"text": result}}, indent=2)


@app.get("/tts")
def tts():
    text = request.query.get("text")
    result = textToSpeech(text=text)
    response.content_type = "application/json"
    return json.dumps(
        {"error": None, "data": {"audio_base64": result, "file_format": "wav"}},
        indent=2,
    )


@app.get("/transcript")
def get_transcript():
    video_id = request.query.get("video_id")
    if video_id is None:
        return json.dumps({"error": "Video id is null", "data": None})
    result = fetchTranscript(video_id)
    response.content_type = "application/json"
    return json.dumps({"error": None, "data": result}, indent=2)


@app.get("/audio")
def get_audio():
    video_id = request.query.get("video_id")
    result = fetchAudio(video_id)
    response.content_type = "application/json"
    return json.dumps({"error": None, "data": result}, indent=2)


@app.get("/stream_audio")
def stream_audio():
    video_id = request.query.get("video_id")
    if not video_id:
        abort(400, "video_id is required")

    safe_video_id = video_id.replace("/", "_").replace("\\", "_")
    file_path = f"./database/audios/{safe_video_id}.mp3"

    if not os.path.exists(file_path):
        abort(404, "Audio not found")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range", None)

    if range_header:
        # Example: "bytes=10000-"
        bytes_range = range_header.replace("bytes=", "").split("-")
        start = int(bytes_range[0])
        end = file_size - 1 if bytes_range[1] == "" else int(bytes_range[1])

        length = end - start + 1

        def stream_partial():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = length
                chunk_size = 1024 * 64
                while remaining > 0:
                    chunk = f.read(min(chunk_size, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        response.status = 206  # Partial content
        response.headers["Content-Type"] = "audio/mpeg"
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response.headers["Content-Length"] = str(length)

        return stream_partial()

    # No range header → send full file
    response.status = 200
    response.headers["Content-Type"] = "audio/mpeg"
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Length"] = str(file_size)

    def stream_full():
        with open(file_path, "rb") as f:
            chunk_size = 1024 * 64
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    return stream_full()


@app.get("/")
def index():
    """
    Simple API documentation for your Bottle server.
    """
    response.content_type = "application/json"

    api_docs = {
        "endpoints": {
            "/": {
                "method": "GET",
                "description": "API documentation",
                "query_params": None,
                "body": None,
                "response": "JSON with available endpoints and description",
            },
            "/stt": {
                "method": "POST",
                "description": "Convert Base64 audio to text",
                "body": {"base64": "Base64-encoded WAV/MP3 audio"},
                "response": {"error": None, "data": {"text": "transcribed text"}},
            },
            "/tts": {
                "method": "GET",
                "description": "Convert text to Base64 WAV audio",
                "query_params": {"text": "Text to convert to speech"},
                "response": {
                    "error": None,
                    "data": {"audio_base64": "<base64>", "file_format": "wav"},
                },
            },
            "/transcript": {
                "method": "GET",
                "description": "Fetch YouTube video transcript",
                "query_params": {"video_id": "YouTube video ID"},
                "response": {"error": None, "data": "transcript text"},
            },
            "/audio": {
                "method": "GET",
                "description": "Fetch YouTube video audio info",
                "query_params": {"video_id": "YouTube video ID"},
                "response": {"error": None, "data": "audio info or URL"},
            },
            "/stream_audio": {
                "method": "GET",
                "description": "Stream audio from local storage (supports Range headers)",
                "query_params": {"video_id": "Video identifier"},
                "response": "Partial or full audio stream",
            },
        }
    }

    return json.dumps(api_docs, indent=2)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=getConfig("PORT"), debug=True)
