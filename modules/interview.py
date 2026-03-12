import random

questions = [
"Tell me about yourself.",
"What are your strengths and weaknesses?",
"Why should we hire you?",
"Explain one project you worked on.",
"Where do you see yourself in five years?"
]

def interview_question():
    return random.choice(questions)