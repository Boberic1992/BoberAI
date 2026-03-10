import threading
import time

from openai_interface import get_openai_response


class TranscriptionManager:
    def __init__(self, update_text_callback):
        self.buffer = []
        self.last_chunk_time = time.time()
        self.update_text = update_text_callback
        self.conversation_history = []

    def add_chunk(self, text):
        if not text.strip():
            return
        self.buffer.append(text)
        self.last_chunk_time = time.time()
        self._process_complete_thought()

    def _process_complete_thought(self):
        if not self.buffer:
            return

        complete_text = " ".join(self.buffer)
        self.buffer = []

        if not complete_text.strip():
            return

        self.update_text("Client:\n" + complete_text)
        self.conversation_history.append({"role": "user", "content": complete_text})
        threading.Thread(target=self._get_ai_response).start()

    def _get_ai_response(self):
        response = get_openai_response(self.conversation_history)
        if response:
            self.update_text("BoberAI:\n" + response)
            self.conversation_history.append({"role": "assistant", "content": response})
