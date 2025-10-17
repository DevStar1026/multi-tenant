from openai import OpenAI
from app.core.config import OPENAI_API_KEY

def run_ai_task(prompt: str):
    if not OPENAI_API_KEY:
        return "AI API key not configured"
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI task failed: {e}"
