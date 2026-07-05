"""
database/init_db.py
--------------------
Creates the SQLite schema for the Fake News Detection application.

Tables:
    users           - login accounts (admin panel)
    predictions     - every prediction made through the app
    logs            - system activity logs
    model_info      - metadata about the currently active ML model
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    article_text TEXT NOT NULL,
    prediction TEXT NOT NULL,           -- 'Fake' or 'Real'
    confidence REAL NOT NULL,           -- 0-100
    fake_probability REAL,
    real_probability REAL,
    top_keywords TEXT,                  -- JSON list
    processing_time_ms REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT,                         -- INFO / WARNING / ERROR
    message TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS model_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT,
    accuracy REAL,
    precision_score REAL,
    recall_score REAL,
    f1_score REAL,
    trained_at TEXT DEFAULT (datetime('now'))
);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()
