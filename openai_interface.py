import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_openai_response(conversation_history):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"
