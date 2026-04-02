import os
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv
from ai_model_hf_backup import ai_response as hf_ai_response

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

SYSTEM_PROMPT = (
    "You are CampusGuide, a friendly and helpful AI assistant for college students. "
    "You help students with campus placements, coding preparation, aptitude questions, "
    "resume building, interview preparation, and career guidance. "
    "Give clear, concise, and practical answers. Use examples when helpful. "
    "Be encouraging and supportive like a real mentor. "
    "Always return plain text only. Do not use markdown symbols like *, #, or backticks. "
    "Ensure answers are complete and do not end abruptly."
)


def _strip_markdown_symbols(text):
    if not text:
        return text

    cleaned = text.replace("**", "")
    cleaned = cleaned.replace("`", "")
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*[*-]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _looks_incomplete(text):
    if not text:
        return True

    t = text.strip()
    if len(t) < 40:
        return True

    bad_endings = (
        "is a",
        "is an",
        "are a",
        "are an",
        "based on",
        "for",
        "with",
        "and",
        "or",
        "to",
        "of",
        "in",
        ":",
        "-",
    )

    lower = t.lower().rstrip()
    return lower.endswith(bad_endings)


def _gemini_response(user_input):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")

    if not gemini_api_key:
        return None

    url = f"{gemini_base_url}/v1beta/models/{gemini_model}:generateContent?key={gemini_api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "parts": [{"text": user_input}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
    }

    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8", errors="replace")
            data = json.loads(body)
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()
            return text or None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print("GEMINI HTTP ERROR:", e.code, error_body)
        return None
    except Exception as e:
        print("GEMINI ERROR:", e)
        return None


def ai_response(user_input):
    load_dotenv(dotenv_path=ENV_PATH, override=True)

    gemini_reply = _gemini_response(user_input)
    if gemini_reply:
        cleaned = _strip_markdown_symbols(gemini_reply)

        # One retry for truncated/formatting-heavy outputs.
        if _looks_incomplete(cleaned) or any(sym in gemini_reply for sym in ["**", "#", "`"]):
            retry_prompt = (
                "Answer the following request again in plain text only. "
                "No markdown symbols. Make sure the response is complete and not cut off.\n\n"
                f"Request:\n{user_input}"
            )
            retry_reply = _gemini_response(retry_prompt)
            if retry_reply:
                retry_cleaned = _strip_markdown_symbols(retry_reply)
                if not _looks_incomplete(retry_cleaned):
                    return retry_cleaned

        return cleaned

    # Backup provider if Gemini fails or is unavailable.
    hf_reply = hf_ai_response(user_input)
    return _strip_markdown_symbols(hf_reply)