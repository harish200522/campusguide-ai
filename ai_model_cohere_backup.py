import os
from dotenv import load_dotenv
import cohere

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

client = cohere.ClientV2(api_key=COHERE_API_KEY)

SYSTEM_PROMPT = (
    "You are CampusGuide, a friendly and helpful AI assistant for college students. "
    "You help students with campus placements, coding preparation, aptitude questions, "
    "resume building, interview preparation, and career guidance. "
    "Give clear, concise, and practical answers. Use examples when helpful. "
    "Be encouraging and supportive like a real mentor."
)

def ai_response(user_input):
    try:
        response = client.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )
        return response.message.content[0].text

    except Exception as e:
        print("AI ERROR:", e)
        return "AI service error. Please try again."
