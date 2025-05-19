import os
from openai import OpenAI
from config import OPENAI_API_KEY, SYSTEM_MESSAGE
import soundfile as sf
import time
from faster_whisper import WhisperModel
from rag_utils import query_codebase

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", OPENAI_API_KEY))
# anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY))
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

def get_openai_response(conversation_history):
    from config import current_interview_mode
    try:
        if current_interview_mode == "Standard":
            messages = [SYSTEM_MESSAGE] + conversation_history[-19:]
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=messages
            )
            return response.choices[0].message.content.strip()
        elif current_interview_mode == "Case Study":
            user_question = conversation_history[-1]['content']
            code_chunks = query_codebase(user_question, top_k=5)
            # Format code context for the system prompt
            code_context = "\n\n".join(
                f"File: {meta['file']} (lines {meta['start_line']}-{meta['end_line']}):\n{doc}"
                for doc, meta in code_chunks
            )
            system_message = {
                "role": "system",
                "content": (
                    "You are an AI assistant answering questions about the following codebase. "
                    "Use the provided code context to answer the user's question.\n\n"
                    f"Code Context:\n{code_context}\n\n"
                    "Answer concisely and reference the code where relevant."
                )
            }
            messages = [system_message] + conversation_history[-19:]
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=messages
            )
            return response.choices[0].message.content.strip()
        else:
            return "Unknown interview mode."
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