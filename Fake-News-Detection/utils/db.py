"""
utils/db.py
-----------
Lightweight SQLite helper functions used across the routes.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "app.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def log_event(level: str, message: str):
    conn = get_conn()
    conn.execute("INSERT INTO logs (level, message) VALUES (?, ?)", (level, message))
    conn.commit()
    conn.close()


def save_prediction(title, article_text, prediction, confidence,
                     fake_probability, real_probability, top_keywords_json,
                     processing_time_ms):
    conn = get_conn()
    conn.execute(
        """INSERT INTO predictions
           (title, article_text, prediction, confidence, fake_probability,
            real_probability, top_keywords, processing_time_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, article_text, prediction, confidence, fake_probability,
         real_probability, top_keywords_json, processing_time_ms),
    )
    conn.commit()
    pred_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pred_id
