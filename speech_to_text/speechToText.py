import os
import base64
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.getConfig import getConfig
from utils.getRandomId import getRandomId

parent_folder = os.path.dirname(os.path.abspath(__file__))

def speechToText(base64_audio=""):
    """
    Converts a base64 audio string to WAV, runs whisper-cli, and returns transcription.
    Works on Windows and Linux.
    """
    if not base64_audio:
        return ""

    is_windows = os.name == "nt"

    # Paths
    whisper_cli = ""
    if is_windows:
        whisper_cli = os.path.join(parent_folder, "windows", "whisper-cli.exe")
    else:
        whisper_cli = os.path.join(parent_folder, "linux", "whisper-cli")

    model_path = os.path.join(parent_folder, "models", getConfig("WHISPER_CPP_MODEL_NAME"))
    wav_path = os.path.join(parent_folder, "samples", f"${getRandomId()}.wav")

    audio_bytes = base64.b64decode(base64_audio)
    with open(wav_path, "wb") as f:
        f.write(audio_bytes)

    command = [
        whisper_cli,
        "-m", model_path,
        "-f", wav_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output_text = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        output_text = e.stderr.strip()

    if os.path.exists(wav_path):
        os.remove(wav_path)

    #[00:00:00.000 --> 00:00:10.500]   And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
    try:
        return output_text.split("]   ")[1]
    except:  # noqa: E722
        return output_text
    

def test():
    file_path = os.path.join(parent_folder, "samples", "jfk.txt")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    result = speechToText(text)
    print(result)

if __name__ == "__main__":
    test()