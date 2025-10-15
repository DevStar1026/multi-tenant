import openai
from app.core.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def run_ai_task(prompt: str):
    if not OPENAI_API_KEY:
        return "AI API key not set"
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
