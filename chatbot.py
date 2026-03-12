from ai_model import ai_response

def chatbot_response(user_input):

    prompt = f"""
You are CampusGuide AI, a placement assistant.

Help students with:
- aptitude preparation
- coding interview preparation
- resume advice
- interview preparation

Student question:
{user_input}
"""

    return ai_response(prompt)