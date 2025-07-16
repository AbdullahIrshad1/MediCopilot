# Updated backend/utils.py
import os
import requests
import re
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL = "deepseek/DeepSeek-R1-0528"
ENDPOINT = "https://models.github.ai/inference/chat/completions"

# Initialize DB
DB_FILE = "chat_history.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_query TEXT,
                response TEXT
            )''')
conn.commit()
conn.close()

def clean_response(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()

def get_medical_advice(user_query: str) -> str:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are MediCopilot, a concise, friendly AI medical assistant. "
                    "Only generate final, clean, structured responses. "
                    "Avoid internal thoughts or speculation. Do NOT use <think>. "
                    "Use bullet points. Suggest safe next steps. Avoid diagnosis."
                )
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
        "max_tokens": 500
    }

    response = requests.post(ENDPOINT, json=body, headers=headers)

    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]
        cleaned = clean_response(result)

        # Save to DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO history (timestamp, user_query, response) VALUES (?, ?, ?)",
                  (datetime.utcnow().isoformat(), user_query, cleaned))
        conn.commit()
        conn.close()

        return cleaned
    else:
        return f"Error: {response.status_code} - {response.text}"

def fetch_history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, user_query, response FROM history ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows
