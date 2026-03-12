import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(api_key=HF_TOKEN)

SYSTEM_PROMPT = (
    "You are CampusGuide, a friendly and helpful AI assistant for college students. "
    "You help students with campus placements, coding preparation, aptitude questions, "
    "resume building, interview preparation, and career guidance. "
    "Give clear, concise, and practical answers. Use examples when helpful. "
    "Be encouraging and supportive like a real mentor."
)

def ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", e)
        return "AI service error. Please try again."