# BoberAI Speech Recognition Chat
## Description
BoberAI Speech Recognition Chat is a versatile desktop application designed for real-time voice-to-text transcription and response generation using OpenAI's language models. It not only transcribes user speech but also has the capability to record audio from the default speaker. This functionality makes it an ideal tool for various interactive situations like virtual meetings, educational lectures, collaborative brainstorming sessions, or casual conversations where capturing and responding to spoken dialogue is valuable.

## Features
* **Voice Recognition:** Transcribes user speech in real-time for instant text representation of verbal communication.
* **Audio Recording:** Capable of recording audio directly from the default speaker, making it suitable for recording and transcribing meetings, lectures, or any spoken interactions.
* **AI-Powered Responses:** Utilizes OpenAI's language models to generate contextually relevant and intelligent responses.
* **Multilingual Support:** Supports English and Serbian language.
* **Interactive GUI:** Offers an intuitive graphical user interface with language-switching capabilities and a clear display of conversation history.

## Usage
Run the application with Python:
```
python main.py
```

## Basic Operations
1. **Voice Recognition:** Press 'R' to start, speak, and release 'R' to transcribe speech.
2. **Audio Capture:** Press 'A' to begin/end recording from the default speaker, suitable for capturing audio during meetings or lectures.
3. **View Transcription and Response:** The transcribed text and AI-generated responses are displayed in the chat window.
4. **Language Switching:** Toggle between languages using the provided buttons.
   
## Configuration
* **Languages:** Default and additional languages can be configured in `config.py`.
* **OpenAI API:** Set up your OpenAI API key for AI interactions in `config.py`.
