from ai_model import ai_response


def _looks_incomplete_reply(text):
    if not text:
        return True

    cleaned = text.strip()
    if len(cleaned) < 60:
        return True

    incomplete_endings = (
        "here",
        "here is",
        "here are",
        "for example",
        "such as",
        "based on",
        "because",
        "and",
        "or",
        ":",
        "-",
    )

    lower = cleaned.lower().rstrip()
    if lower.endswith(incomplete_endings):
        return True

    return False

def chatbot_response(user_input, resume_context=None):

    resume_section = ""
    if resume_context:
        resume_section = f"""
Uploaded resume context (use this when the question is about resume/profile/jobs/projects/skills):
---
{resume_context}
---
"""

    prompt = f"""
You are CampusGuide AI, a placement assistant.

Help students with:
- aptitude preparation
- coding interview preparation
- resume advice
- interview preparation

Rules:
- If the question is about the student's resume, profile, projects, strengths, weaknesses, or improvements, answer using the uploaded resume context below.
- If resume context is missing for a resume-related question, politely ask the student to upload a resume.
- Do not claim you cannot see the resume if context is provided.
- Focus on answering the current question directly; do not repeat a generic resume introduction.
- Keep the response specific, practical, and concise (use bullets when helpful).
- If mentioning resume details, quote concrete points from the provided context.

{resume_section}

Student question:
{user_input}
"""

    reply = ai_response(prompt)

    if _looks_incomplete_reply(reply):
        retry_prompt = f"""
Your previous response appears incomplete.

Answer the student's question again with a complete response.
- Start directly with useful points.
- Give at least 4 concrete bullet points.
- Keep it fully self-contained and finish properly.

Student question:
{user_input}

Resume context:
{resume_context or 'Not provided'}
"""
        retry_reply = ai_response(retry_prompt)
        if retry_reply and not _looks_incomplete_reply(retry_reply):
            return retry_reply

    return reply