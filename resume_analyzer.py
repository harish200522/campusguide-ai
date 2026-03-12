import PyPDF2
from ai_model import ai_response

def extract_text_from_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text.strip()

def analyze_resume(file):
    text = extract_text_from_pdf(file)

    if not text:
        return "Could not extract text from the resume. Please upload a valid PDF."

    prompt = f"""Analyze the following student resume thoroughly and provide:

1. **Skills Detected** - List all technical and soft skills found
2. **Strengths** - What's good about this resume
3. **Weaknesses** - What's missing or needs improvement
4. **Suggestions** - Specific actionable tips to improve this resume for placements
5. **Overall Rating** - Rate the resume out of 10 for placement readiness

Here is the resume content:
---
{text}
---

Give a detailed, helpful, and encouraging analysis."""

    return ai_response(prompt)