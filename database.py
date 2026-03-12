import sqlite3

def init_db():

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_chat(user, bot):

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chats (user_message, bot_response) VALUES (?, ?)",
        (user, bot)
    )

    conn.commit()
    conn.close()


def get_chats():

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, user_message FROM chats ORDER BY id DESC")

    chats = cursor.fetchall()

    conn.close()

    return chats


def get_chat_by_id(chat_id):

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_message, bot_response FROM chats WHERE id=?",
        (chat_id,)
    )

    chat = cursor.fetchone()

    conn.close()

    return chat


def delete_chat_by_id(chat_id):

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()