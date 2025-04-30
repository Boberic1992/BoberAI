import time
import threading
from openai_interface import get_openai_response

class TranscriptionManager:
    def __init__(self, update_text_callback=None):
        self.buffer = []
        self.last_chunk_time = time.time()
        self.update_text = update_text_callback
        self.conversation_history = []
        self.pending_transcription = False
        
    def add_chunk(self, text):
        if not text.strip():
            return
            
        self.buffer.append(text)
        current_time = time.time()

        self.process_complete_thought()
            
        self.last_chunk_time = current_time
        
    def process_complete_thought(self):
        if not self.buffer:
            return
            
        complete_text = " ".join(self.buffer)
        if complete_text.strip():
            self.update_text("Client:\n" + complete_text)
            self.conversation_history.append({"role": "user", "content": complete_text})
            # Start response generation in a separate thread
            threading.Thread(target=self._get_ai_response, args=(complete_text,)).start()
                
        self.buffer = []

    def _get_ai_response(self, text):
        response = get_openai_response(self.conversation_history)
        if response is not None:
            self.update_text("BoberAI:\n" + response)
            self.conversation_history.append({"role": "assistant", "content": response})
            
            