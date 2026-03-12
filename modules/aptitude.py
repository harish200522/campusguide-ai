import random

questions = [
"A train travels 120 km in 2 hours. What is its speed?",
"A father is twice the age of his son. After 10 years their ages sum to 70. Find son's age.",
"If 5 workers complete a job in 10 days, how many days will 10 workers take?"
]

def aptitude_question():
    return random.choice(questions)