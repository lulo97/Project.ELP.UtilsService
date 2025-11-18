import os
import base64
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.getConfig import getConfig
from utils.getRandomId import getRandomId

parent_folder = os.path.dirname(os.path.abspath(__file__))

samples_folder = os.path.join(parent_folder, "samples")
os.makedirs(samples_folder, exist_ok=True)

def textToSpeech(text=""):
    """
    Converts text to speech using Piper TTS and returns Base64-encoded WAV audio.
    Works on Windows and Linux.
    """
    if not text:
        return ""

    # Path to Piper module
    piper_module = "piper"  # using python -m piper

    # Model path
    model_path = os.path.join(parent_folder, "models", getConfig("PIPER_TTS_MODEL_NAME"))

    # Random WAV filename
    wav_filename = f"{getRandomId()}.wav"
    wav_path = os.path.join(samples_folder, wav_filename)

    # Build command
    command = [
        sys.executable, "-m", piper_module,
        "-m", model_path,
        "-f", wav_path,
        "--",
        text
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Error generating TTS:", e.stderr.strip())
        return ""

    # Read WAV and convert to Base64
    try:
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print("Error reading WAV file:", e)
        audio_base64 = ""
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

    return audio_base64


def test():
    sample_text = "Please use our dedicated channels for questions and discussion."
    result_base64 = textToSpeech(sample_text)
    print(result_base64)

if __name__ == "__main__":
    test()
