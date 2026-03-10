# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BoberAI is a Windows-only desktop app for real-time voice transcription and AI-powered responses, built with tkinter and OpenAI APIs. Designed for interview prep, meetings, and code assistance with English/Serbian language support.

## Running the App

```bash
# Activate venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate   # Git Bash on Windows

# Install dependencies
pip install -r requirements.txt

# Run (requires .env with OPENAI_API_KEY)
python main.py
```

No test suite or linting setup exists in this project.

## Architecture

The app follows a callback-driven architecture with global mutable state for settings and recording state.

**Entry point:** `main.py` — creates the tkinter window, wires up GUI elements, event handlers, and the speech module's update callback.

**Core flow:**
1. `speech.py` is the central module — owns recording state, conversation history, audio processing (`AudioProcessor`), and coordinates transcription + AI responses
2. Audio is captured via `soundcard` (loopback from system speaker), chunked by silence detection in `AudioProcessor`, then transcribed
3. Transcription uses either local `faster-whisper` (English) or OpenAI API `gpt-4o-mini-transcribe` (Serbian), selected by `config.current_language`
4. `TranscriptionManager` (`transcription_manager.py`) buffers transcription chunks, assembles complete thoughts, and triggers AI responses via `openai_interface.get_openai_response`
5. AI responses go through `openai_interface.py` using `gpt-4.1-mini` with conversation history (last 19 messages + system prompt)
6. All UI updates flow through `speech.update_callback` → `main.update_text()` which renders to the tkinter ScrolledText widget

**GUI layer:**
- `window_setup.py` — window config, capture protection via Win32 API (`SetWindowDisplayAffinity`)
- `gui_elements.py` — conversation display, info label, settings panel (language/framework/mode radio buttons)
- `event_handlers.py` — keyboard bindings: Ctrl+Shift+S (screenshot explain), Ctrl+Shift+D (screenshot debug), Ctrl+Shift+H (toggle visibility), A (toggle recording)

**Configuration:** `config.py` — global mutable state for language, programming language, interview mode. Settings changed via GUI radio buttons → setter functions.

**RAG (not yet wired up):** `embeded_codebase.py` (run as `python embeded_codebase.py`) generates ChromaDB embeddings from a `code_chunks_manifest.json`; `rag_utils.py` queries them. The "Case Study" interview mode UI exists but is not connected to the RAG backend yet.

## Key Patterns

- Threading is used extensively: audio recording, transcription, AI response generation, and screenshot processing all run in separate threads
- The `update_text` callback chain (`speech` → `main`) is the only safe way to update the GUI from worker threads
- Message prefixes (`BoberAI:`, `Me:`, `Client:`, `[INFO]`, `[REC]`) control how text is displayed/routed in the UI
- Screenshot features temporarily hide the window (alpha=0), capture screen via PIL, then send base64 to OpenAI vision API

## Platform Dependencies

This app is Windows-only due to:
- `ctypes.windll` / `win32con` for capture protection
- `soundcard` loopback recording from Windows default speaker
- `pywin32` package
