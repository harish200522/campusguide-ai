import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from chatbot import chatbot_response
from database import init_db, save_chat, get_chats, get_chat_by_id, delete_chat_by_id
from resume_analyzer import extract_text_from_pdf, analyze_resume_text

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "campusguide-dev-secret")

# initialize database
init_db()


def build_resume_context(text, max_chars=2500):
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = "\n".join(cleaned_lines)

    if len(cleaned_text) <= max_chars:
        return cleaned_text

    head_len = int(max_chars * 0.7)
    tail_len = max_chars - head_len - 20
    return f"{cleaned_text[:head_len]}\n...\n{cleaned_text[-tail_len:]}"


# ==========================
# Home Page
# ==========================
@app.route("/")
def home():
    # Start a fresh active conversation on each page load/refresh.
    session.pop("active_chat_id", None)

    chats = get_chats()

    return render_template("index.html", chats=chats)


# ==========================
# Chatbot Response
# ==========================
@app.route("/get", methods=["POST"])
def get_response():

    user_message = request.form["msg"]
    resume_context = session.get("uploaded_resume_context")

    # Backward compatibility for already-active sessions created before this fix.
    if not resume_context and session.get("uploaded_resume_text"):
        resume_context = build_resume_context(session.get("uploaded_resume_text"))
        session["uploaded_resume_context"] = resume_context
        session.pop("uploaded_resume_text", None)

    bot_reply = chatbot_response(user_message, resume_context=resume_context)
    active_chat_id = session.get("active_chat_id")

    # save all turns under one active conversation
    saved_chat_id = save_chat(user_message, bot_reply, chat_id=active_chat_id)
    session["active_chat_id"] = saved_chat_id

    return bot_reply


# ==========================
# Load Previous Chat
# ==========================
@app.route("/chat/<int:chat_id>")
def load_chat(chat_id):

    chat = get_chat_by_id(chat_id)

    if not chat:
        session.pop("active_chat_id", None)
        return jsonify({"messages": []})

    # Continue this chat thread for subsequent user messages.
    session["active_chat_id"] = chat_id

    return jsonify(chat)


# ==========================
# Resume Upload Analyzer
# ==========================
@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    file = request.files.get("resume")
    user_message = request.form.get("msg", "").strip()

    if not file or file.filename == "":
        return "No file uploaded"

    resume_text = extract_text_from_pdf(file)
    if not resume_text:
        return "Could not extract text from the resume. Please upload a valid PDF."

    resume_context = build_resume_context(resume_text)
    session["uploaded_resume_context"] = resume_context
    session.pop("uploaded_resume_text", None)

    if user_message:
        result = chatbot_response(user_message, resume_context=resume_context)
        active_chat_id = session.get("active_chat_id")
        saved_chat_id = save_chat(f"{user_message} (with resume: {file.filename})", result, chat_id=active_chat_id)
        session["active_chat_id"] = saved_chat_id
    else:
        result = analyze_resume_text(resume_text)
        active_chat_id = session.get("active_chat_id")
        saved_chat_id = save_chat("Uploaded resume: " + file.filename, result, chat_id=active_chat_id)
        session["active_chat_id"] = saved_chat_id

    return result


# ==========================
# Delete Chat
# ==========================
@app.route("/delete_chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):

    try:
        delete_chat_by_id(chat_id)
        return "Chat deleted successfully"
    except Exception as e:
        print(f"Error deleting chat {chat_id}: {e}")
        return f"Error: {str(e)}", 500


@app.route("/new_chat_session", methods=["POST"])
def new_chat_session():
    session.pop("active_chat_id", None)
    return "OK"


# ==========================
# Run Server
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)