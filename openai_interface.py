import os
import tempfile

import soundfile as sf
from openai import OpenAI

import config
from config import OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", OPENAI_API_KEY))


def get_openai_response(conversation_history):
    try:
        messages = [config.get_system_message()] + conversation_history[-19:]
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"


def transcribe_audio(audio_data, sample_rate, language="en"):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name
        sf.write(temp_path, audio_data, sample_rate)

        with open(temp_path, "rb") as audio_file:
            return client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file,
                response_format="text",
                language=language
            )

    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
