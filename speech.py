import threading
import time
import soundcard as sc
import numpy as np
from config import SAMPLE_RATE
from transcription_manager import TranscriptionManager
from openai_interface import get_openai_response, transcribe_audio, transcribe_audio_sr
import warnings
from soundcard.mediafoundation import SoundcardRuntimeWarning

warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="Bad certificate in Windows certificate store")


is_recording = False
stop_recording = threading.Event()
conversation_history = []
is_audio_recording = False
start_time = None

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
    global conversation_history
    update_text("Me:\n" + text)

    conversation_history.append({"role": "user", "content": text})

    # Odgovor od AI
    response = get_openai_response(conversation_history)
    update_text("BoberAI:\n" + response)

    # Appenduj
    conversation_history.append({"role": "assistant", "content": response})

    time.sleep(0.5)



pause_audio_recording = False


def process_screenshot(base64_image):
    def async_process():
        global conversation_history, pause_audio_recording
        
        # pause audio recording if it's active
        was_recording = False
        if is_audio_recording:
            was_recording = True
            pause_audio_recording = True
            update_text("[INFO]Paused audio recording for screenshot analysis...")
        
        try:
            from config import current_prog_language
            message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"You will find in a picture a {current_prog_language} coding task. Please:\n\n"
                                "1. **Task Analysis**: Identify what needs to be implemented\n"
                                f"2. **{current_prog_language} Solution**: Provide a complete working solution using {current_prog_language}, also in each line of code, include a comment explaining why that line is used\n"
                                "3. **Code Explanation**: Explain how your solution works\n"
                                "4. **Edge Cases**: List potential edge cases and how your solution handles them\n\n"
                                "Format your response using Markdown:\n"
                                f"- Use ```{current_prog_language} for code blocks\n"
                                "- Use bullet points for key points\n"
                                "- Use headers for sections\n"
                                f"Focus on producing correct, efficient, and well-documented {current_prog_language} code."
                    },
                    {   
                        # "type": "image", # for anthropic
                        "type": "image_url", # for open ai
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                        # "source": {
                        #     "type": "base64",
                        #     "media_type": "image/png",
                        #     "data": base64_image
                        # }
                    }
                ]
            }
            
            update_text(f"Me:\n[{current_prog_language} code task screenshot sent]")
            conversation_history.append(message)
            
            update_text("[INFO]Processing screenshot...")
            response = get_openai_response(conversation_history)
            update_text("BoberAI:\n" + response)
            conversation_history.append({"role": "assistant", "content": response})
            
        finally:
            # resume audio recording if it was active before
            if was_recording:
                pause_audio_recording = False
                update_text("[INFO]Resumed audio recording")
    
    threading.Thread(target=async_process).start()

def debug_screenshot(base64_image):
    def async_debug():
        global conversation_history, pause_audio_recording
        
        was_recording = False
        if is_audio_recording:
            was_recording = True
            pause_audio_recording = True
            update_text("[INFO]Paused audio recording for code debugging...")

        try:
            from config import current_prog_language
            message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"This image contains {current_prog_language} code that may have bugs or issues.\n\n"
                                "Your tasks are:\n"
                                "1. **Identify Errors**: Analyze the code and detect any syntax, logic, or runtime issues\n"
                                f"2. **Fix the Code**: Provide a corrected version in {current_prog_language}, also in each line of code, include a comment explaining why that line is used\n"
                                "3. **Explain Fixes**: Briefly describe what was wrong and how it was fixed\n"
                                "4. **Edge Cases**: List potential edge cases and how your solution handles them\n\n"
                                "Format your response using Markdown:\n"
                                f"- Use ```{current_prog_language} for code blocks\n"
                                "- Bullet points for error explanations\n"
                                "- Use section headers where appropriate\n"
                                "Be concise and focus only on what is needed to get the code working correctly."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }

            update_text(f"Me:\n[Debugging {current_prog_language} code screenshot sent]")
            conversation_history.append(message)
            
            update_text("[INFO]Analyzing code for bugs...")
            response = get_openai_response(conversation_history)
            update_text("BoberAI:\n" + response)
            conversation_history.append({"role": "assistant", "content": response})
        
        finally:
            if was_recording:
                pause_audio_recording = False
                update_text("[INFO]Resumed audio recording")
    
    threading.Thread(target=async_debug).start()


class AudioProcessor:
    def __init__(self):
        self.CHUNK_DURATION = 1.0
        self.SILENCE_THRESHOLD = 0.01
        self.PAUSE_THRESHOLD = 0.5
        self.buffer = []
        self.processing_buffer = []
        self.last_voice_time = None
    
    def detect_silence(self, audio_chunk):
        """Check if audio chunk contains silence"""
        return np.max(np.abs(audio_chunk)) < self.SILENCE_THRESHOLD
    
    def process_chunk(self, audio_chunk):
        is_silence = self.detect_silence(audio_chunk)
        current_time = time.time()
        
        if not is_silence:
            self.buffer.append(audio_chunk)
            self.last_voice_time = current_time
            return False
        elif self.last_voice_time and (current_time - self.last_voice_time > self.PAUSE_THRESHOLD):
            if len(self.buffer) > 0:
                self.processing_buffer = self.buffer.copy()
                self.buffer = []
                return True
        return False

def continuous_audio_recording():
    global is_audio_recording
    processor = AudioProcessor()
    transcription_manager = TranscriptionManager(update_text)
    transcription_manager.conversation_history = conversation_history
    
    try:
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(
            samplerate=SAMPLE_RATE
        ) as mic:
            while is_audio_recording:
                if pause_audio_recording:
                    time.sleep(0.1)
                    continue
                
                audio_chunk = mic.record(numframes=int(SAMPLE_RATE * processor.CHUNK_DURATION))
                
                if processor.process_chunk(audio_chunk):
                    def process_audio():
                        try:
                            full_audio = np.concatenate(processor.processing_buffer)
                            # use the appropriate transcription function based on language
                            from config import current_language
                            text = transcribe_audio_sr(full_audio, SAMPLE_RATE) if current_language == "sr" else transcribe_audio(full_audio, SAMPLE_RATE)
                            
                            if text and text.strip():
                                word_count = len(text.split())
                                if word_count > 2:
                                    transcription_manager.add_chunk(text)
                        except Exception as e:
                            update_text(f"[ERROR] Transcription failed: {str(e)}")
                    
                    threading.Thread(target=process_audio).start()
    
    except Exception as e:
        update_text(f"[ERROR] Recording failed: {str(e)}")