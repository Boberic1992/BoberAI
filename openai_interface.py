import os
from openai import OpenAI
from config import OPENAI_API_KEY, SYSTEM_MESSAGE
import soundfile as sf
import time
from faster_whisper import WhisperModel

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", OPENAI_API_KEY))
# anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY))
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

def get_openai_response(conversation_history):
    try:
        # check if the message contains an image  
        latest_message = conversation_history[-1]
        if isinstance(latest_message.get('content'), list):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[latest_message]
                # max_tokens=500
            )
        else:
            if not conversation_history or conversation_history[0].get('role') != 'system':
                conversation_history.insert(0, SYSTEM_MESSAGE)

            # always keep the first message, and limit total to 20
            conversation_history = [conversation_history[0]] + conversation_history[-19:]
            # print(f'Conversation history: {conversation_history}')
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=conversation_history
            )
            
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

def transcribe_audio_sr(audio_data, sample_rate):
    """Transcribe audio using OpenAI's Whisper API"""
    try:
        temp_path = f"temp_audio_{int(time.time() * 1000)}.wav"
        sf.write(temp_path, audio_data, sample_rate)
        
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe", # gpt-4o-mini-transcribe whisper-1
                file=audio_file,
                response_format="text",
                # serbian languagne
                language="sr"
            )
        
        os.remove(temp_path)
        return transcript
        
    except Exception as e:
        print(f"[ERROR] Whisper API transcription failed: {str(e)}")
        return None


def transcribe_audio(audio_data, sample_rate):
    """Transcribe audio using local Whisper model"""
    try:
        temp_path = f"temp_audio_{int(time.time() * 1000)}.wav"
        sf.write(temp_path, audio_data, sample_rate)
        segments, _ = whisper_model.transcribe(
            temp_path,
            language='en',
            beam_size=1
        )
        
        # combine all text parts into one big text
        transcript = " ".join([segment.text for segment in segments])
        
        os.remove(temp_path)
        return transcript.strip()
        
    except Exception as e:
        print(f"[ERROR] Local Whisper transcription failed: {str(e)}")
        return None