import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from chatbot import chatbot_response
from database import init_db, save_chat, get_chats, get_chat_by_id, delete_chat_by_id
from resume_analyzer import analyze_resume

load_dotenv()

app = Flask(__name__)

# initialize database
init_db()


# ==========================
# Home Page
# ==========================
@app.route("/")
def home():

    chats = get_chats()

    return render_template("index.html", chats=chats)


# ==========================
# Chatbot Response
# ==========================
@app.route("/get", methods=["POST"])
def get_response():

    user_message = request.form["msg"]

    bot_reply = chatbot_response(user_message)

    # save chat to database
    save_chat(user_message, bot_reply)

    return bot_reply


# ==========================
# Load Previous Chat
# ==========================
@app.route("/chat/<int:chat_id>")
def load_chat(chat_id):

    chat = get_chat_by_id(chat_id)

    return jsonify({
        "user": chat[0],
        "bot": chat[1]
    })


# ==========================
# Resume Upload Analyzer
# ==========================
@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    file = request.files.get("resume")

    if not file or file.filename == "":
        return "No file uploaded"

    result = analyze_resume(file)

    # save to chat history
    save_chat("Analyze my resume: " + file.filename, result)

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


# ==========================
# Run Server
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)