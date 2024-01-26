import speech_recognition as sr
from pynput import keyboard
import threading
import time
import soundcard as sc
import soundfile as sf
import numpy as np
from config import SAMPLE_RATE, DEFAULT_LANGUAGE
from openai_interface import get_openai_response

is_recording = False
stop_recording = threading.Event()
conversation_history = []
is_audio_recording = False
start_time = None

recognizer = sr.Recognizer()

update_callback = None

def set_update_callback(callback):
    global update_callback
    update_callback = callback

def update_text(message):
    if update_callback:
        update_callback(message)
    else:
        print(message)

def record_mic():
    global is_recording, DEFAULT_LANGUAGE, conversation_history
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while not stop_recording.is_set():
            if is_recording:
                update_text(f"[REC]Recording in {DEFAULT_LANGUAGE}... Speak now.")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio, language=DEFAULT_LANGUAGE)
                    update_text("Me:\n" + text)


                    conversation_history.append({"role": "user","content":text})

                    # Odgovor od AI
                    response = get_openai_response(conversation_history)
                    update_text("BoberAI:\n" + response)

                    # Dodaj konverzaciju
                    conversation_history.append({"role":"assistant", "content":response})

                except sr.UnknownValueError:
                    update_text("[INFO]Could not understand audio")
                except sr.RequestError as e:
                    update_text(f"[INFO]Could not request results; {e}")
                except sr.WaitTimeoutError:
                    update_text("[INFO]No speech detected within the time limit.")
                finally:
                    is_recording = False

            time.sleep(0.5)

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

def record_audio():
    global is_audio_recording, start_time
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
        update_text(f"[REC]Recording audio in {DEFAULT_LANGUAGE}.")
        is_audio_recording = True
        audio_data = []
        while is_audio_recording:

            audio_chunk = mic.record(numframes=SAMPLE_RATE // 10)
            audio_data.append(audio_chunk)

            # Limit na 1 minut
            if time.time() - start_time >= 60:  
                break

    audio_data = np.concatenate(audio_data, axis=0)

    time.sleep(0.5)
    
    # Save
    filename = "recorded_audio.wav"
    sf.write(file=filename, data=audio_data, samplerate=SAMPLE_RATE)

    # Transcribe
    transcribe_audio(filename)


def transcribe_audio(filename):
    global conversation_history
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            update_text("[INFO] Recognizing...")
            text = recognizer.recognize_google(audio, language=DEFAULT_LANGUAGE)
            conversation_history.append({"role": "user", "content": text})
            update_text("Client:\n" + text)

            response = get_openai_response(conversation_history)
            if response is not None:
                update_text("BoberAI:\n" + response)
                conversation_history.append({"role": "assistant", "content": response})
            else:
                update_text("[ERROR] No response from OpenAI.")

        except sr.UnknownValueError:
            update_text("[INFO] Speech Recognition could not understand audio")
            update_text("[INFO] Could not understand audio")
        except sr.RequestError as e:
            update_text(f"[INFO] Could not request results from Speech Recognition service; {e}")
            update_text(f"[INFO] Could not request results; {e}")



def main():
    global conversation_history
    conversation_history = [
    {
        "role": "system",
        "content": (
            "You will receive questions transcribed from audio, which may not always be complete. "
            "Your task is to understand these questions and answer them clearly and concisely. "
            "Answer shouldn't be bigger then 100 words."
            "The questions can be in either Serbian or English. "
            "Responses may include code snippets, which should be clearly formatted."
            "If a message starts with 'Client:', consider it a question or statement from the client, "
            "and respond accordingly. If it's a statement or request for an explanation, provide a brief explanation."
        )
    }
    ]

if __name__ == "__main__":
    main()
