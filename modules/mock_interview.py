questions = [
"Welcome to the mock interview.",
"Tell me about yourself.",
"Explain your final year project.",
"What are your strengths?",
"Why should we hire you?",
"Where do you see yourself in five years?"
]

index = 0

def mock_interview():
    global index

    if index < len(questions):
        q = questions[index]
        index += 1
        return q
    else:
        return "Mock interview completed. Good luck for your placements!"