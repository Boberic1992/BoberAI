import os
import tempfile
import time

import soundfile as sf
from faster_whisper import WhisperModel
from openai import OpenAI

from config import OPENAI_API_KEY, SYSTEM_MESSAGE

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", OPENAI_API_KEY))
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")


def get_openai_response(conversation_history):
    try:
        messages = [SYSTEM_MESSAGE] + conversation_history[-19:]
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"


def transcribe_audio(audio_data, sample_rate, language="en"):
    """Transcribe audio using local Whisper for English, OpenAI API for Serbian."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name
        sf.write(temp_path, audio_data, sample_rate)

        if language == "sr":
            with open(temp_path, "rb") as audio_file:
                return client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file,
                    response_format="text",
                    language="sr"
                )
        else:
            segments, _ = whisper_model.transcribe(
                temp_path,
                language="en",
                beam_size=1
            )
            return " ".join(seg.text for seg in segments).strip()

    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
