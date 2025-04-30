# BoberAI Assistant

## Description
BoberAI Assistant is a desktop application that combines real-time voice transcription, speaker audio recording, and AI-powered responses. It's designed for interview preparation, meetings, lectures, and general AI assistance with support for both English and Serbian languages.

## Features
- **Voice Recognition**: Real-time speech-to-text transcription
- **Speaker Recording**: Capture audio from your computer's default speaker
- **AI-Powered Responses**: Uses OpenAI's GPT models for intelligent interactions
- **Code Analysis**: Screenshot any code to get explanations or debugging help
- **Multilingual**: Supports English and Serbian
- **Programming Help**: Specialized assistance for Python and SQL code
- **Capture Protection**: Window capture protection for secure usage

## Requirements
- Windows OS
- Python 3.8+
- OpenAI API key
- System audio devices (microphone and speakers)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the root directory:
```env
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Starting the Application
```bash
python main.py
```

### Keyboard Controls
- **A**: Start/Stop audio recording from system speaker
- **Ctrl+Shift+S**: Take screenshot for code explanation
- **Ctrl+Shift+D**: Take screenshot for code debugging
- **Ctrl+Shift+H**: Toggle window visibility

### Settings Panel
- Toggle between English and Serbian languages
- Switch between Python and SQL code analysis

## Security Notes
- The window is protected against screen capture
- API keys should be stored in `.env` file
- Never commit `.env` file to version control

## Dependencies
See `requirements.txt` for complete list of dependencies.