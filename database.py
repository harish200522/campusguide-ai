import os
import sqlite3
import json


def _get_db_path():
    db_path = os.environ.get("DATABASE_PATH", "chat_history.db").strip()
    return db_path or "chat_history.db"


def _connect():
    db_path = _get_db_path()
    db_dir = os.path.dirname(db_path)

    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    return sqlite3.connect(db_path)

def init_db():

    conn = _connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT,
        title TEXT,
        messages_json TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(chats)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    if "title" not in existing_cols:
        cursor.execute("ALTER TABLE chats ADD COLUMN title TEXT")
    if "messages_json" not in existing_cols:
        cursor.execute("ALTER TABLE chats ADD COLUMN messages_json TEXT")

    conn.commit()
    conn.close()


def save_chat(user, bot, chat_id=None):

    conn = _connect()
    cursor = conn.cursor()

    if chat_id:
        cursor.execute("SELECT messages_json FROM chats WHERE id=?", (chat_id,))
        row = cursor.fetchone()

        messages = []
        if row and row[0]:
            try:
                messages = json.loads(row[0])
            except json.JSONDecodeError:
                messages = []

        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})

        cursor.execute(
            "UPDATE chats SET messages_json=?, bot_response=? WHERE id=?",
            (json.dumps(messages), bot, chat_id)
        )

        conn.commit()
        conn.close()
        return chat_id

    messages = [
        {"role": "user", "content": user},
        {"role": "assistant", "content": bot}
    ]
    title = (user or "New Chat").strip()[:80]

    cursor.execute(
        "INSERT INTO chats (user_message, bot_response, title, messages_json) VALUES (?, ?, ?, ?)",
        (user, bot, title, json.dumps(messages))
    )

    new_chat_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return new_chat_id


def get_chats():

    conn = _connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, COALESCE(NULLIF(title, ''), NULLIF(user_message, ''), 'New Chat')
        FROM chats
        ORDER BY id DESC
        """
    )

    chats = cursor.fetchall()

    conn.close()

    return chats


def get_chat_by_id(chat_id):

    conn = _connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_message, bot_response, messages_json FROM chats WHERE id=?",
        (chat_id,)
    )

    chat = cursor.fetchone()

    conn.close()

    if not chat:
        return None

    user_message, bot_response, messages_json = chat

    if messages_json:
        try:
            messages = json.loads(messages_json)
            return {"messages": messages}
        except json.JSONDecodeError:
            pass

    return {
        "messages": [
            {"role": "user", "content": user_message or ""},
            {"role": "assistant", "content": bot_response or ""}
        ]
    }


def delete_chat_by_id(chat_id):

    conn = _connect()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()