import threading
import time
import warnings

import numpy as np
import soundcard as sc
from soundcard.mediafoundation import SoundcardRuntimeWarning

from config import SAMPLE_RATE, current_language, current_prog_language
from openai_interface import get_openai_response, transcribe_audio
from transcription_manager import TranscriptionManager

warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="Bad certificate in Windows certificate store")

is_recording = False
is_audio_recording = False
pause_audio_recording = False
conversation_history = []
update_callback = None


def set_update_callback(callback):
    global update_callback
    update_callback = callback


def update_text(message):
    if update_callback:
        update_callback(message)
    else:
        print(message)


def process_typed_message(text):
    update_text("Me:\n" + text)
    conversation_history.append({"role": "user", "content": text})

    response = get_openai_response(conversation_history)
    update_text("BoberAI:\n" + response)
    conversation_history.append({"role": "assistant", "content": response})


def _with_paused_recording(fn):
    """Run fn while audio recording is paused, then resume."""
    global pause_audio_recording
    was_recording = is_audio_recording
    if was_recording:
        pause_audio_recording = True

    try:
        fn()
    finally:
        if was_recording:
            pause_audio_recording = False
            update_text("[INFO]Resumed audio recording")


def _process_screenshot_impl(base64_image, prompt_text, display_label):
    def work():
        import config
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text.format(lang=config.current_prog_language)},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                }
            ]
        }

        update_text(f"Me:\n[{display_label.format(lang=config.current_prog_language)}]")
        conversation_history.append(message)

        update_text("[INFO]Processing screenshot...")
        response = get_openai_response(conversation_history)
        update_text("BoberAI:\n" + response)
        conversation_history.append({"role": "assistant", "content": response})

    def run():
        if is_audio_recording:
            update_text("[INFO]Paused audio recording for screenshot analysis...")
        _with_paused_recording(work)

    threading.Thread(target=run).start()


EXPLAIN_PROMPT = (
    "You will find in a picture a {lang} coding task. Please:\n\n"
    "1. **Task Analysis**: Identify what needs to be implemented\n"
    "2. **{lang} Solution**: Provide a complete working solution using {lang}, "
    "also in each line of code, include a comment explaining why that line is used\n"
    "3. **Code Explanation**: Explain how your solution works\n"
    "4. **Edge Cases**: List potential edge cases and how your solution handles them\n\n"
    "Format your response using Markdown:\n"
    "- Use ```{lang} for code blocks\n"
    "- Use bullet points for key points\n"
    "- Use headers for sections\n"
    "Focus on producing correct, efficient, and well-documented {lang} code."
)

DEBUG_PROMPT = (
    "This image contains {lang} code that may have bugs or issues.\n\n"
    "Your tasks are:\n"
    "1. **Identify Errors**: Analyze the code and detect any syntax, logic, or runtime issues\n"
    "2. **Fix the Code**: Provide a corrected version in {lang}, "
    "also in each line of code, include a comment explaining why that line is used\n"
    "3. **Explain Fixes**: Briefly describe what was wrong and how it was fixed\n"
    "4. **Edge Cases**: List potential edge cases and how your solution handles them\n\n"
    "Format your response using Markdown:\n"
    "- Use ```{lang} for code blocks\n"
    "- Bullet points for error explanations\n"
    "- Use section headers where appropriate\n"
    "Be concise and focus only on what is needed to get the code working correctly."
)


def process_screenshot(base64_image):
    _process_screenshot_impl(base64_image, EXPLAIN_PROMPT, "{lang} code task screenshot sent")


def debug_screenshot(base64_image):
    _process_screenshot_impl(base64_image, DEBUG_PROMPT, "Debugging {lang} code screenshot sent")


class AudioProcessor:
    def __init__(self):
        self.CHUNK_DURATION = 0.3
        self.SILENCE_THRESHOLD = 0.005
        self.PAUSE_THRESHOLD = 1.0
        self.buffer = []
        self.last_voice_time = None

    def process_chunk(self, audio_chunk):
        is_silence = np.max(np.abs(audio_chunk)) < self.SILENCE_THRESHOLD
        current_time = time.time()

        if not is_silence:
            self.buffer.append(audio_chunk)
            self.last_voice_time = current_time
            return None

        if self.last_voice_time and (current_time - self.last_voice_time > self.PAUSE_THRESHOLD):
            if self.buffer:
                # Capture buffer contents before clearing to avoid race condition
                ready_buffer = self.buffer.copy()
                self.buffer = []
                return ready_buffer

        return None


def continuous_audio_recording():
    global is_audio_recording
    processor = AudioProcessor()
    transcription_manager = TranscriptionManager(update_text)
    transcription_manager.conversation_history = conversation_history

    try:
        mic = sc.get_microphone(
            id=str(sc.default_speaker().name), include_loopback=True
        )
        with mic.recorder(samplerate=SAMPLE_RATE) as recorder:
            while is_audio_recording:
                if pause_audio_recording:
                    time.sleep(0.1)
                    continue

                audio_chunk = recorder.record(
                    numframes=int(SAMPLE_RATE * processor.CHUNK_DURATION)
                )
                ready_buffer = processor.process_chunk(audio_chunk)

                if ready_buffer is not None:
                    _process_audio_chunk(ready_buffer, transcription_manager)
                else:
                    time.sleep(0.1)

    except Exception as e:
        update_text(f"[ERROR] Recording failed: {e}")


def _process_audio_chunk(audio_buffer, transcription_manager):
    def work():
        try:
            import config
            full_audio = np.concatenate(audio_buffer)
            text = transcribe_audio(full_audio, SAMPLE_RATE, language=config.current_language)

            if text and text.strip() and len(text.split()) > 2:
                transcription_manager.add_chunk(text)
        except Exception as e:
            update_text(f"[ERROR] Transcription failed: {e}")

    threading.Thread(target=work).start()
