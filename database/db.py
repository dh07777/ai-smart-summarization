import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

import config

MAX_STORED_CHARS = 20_000


@contextmanager
def _conn():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_type TEXT NOT NULL,
                original_text TEXT,
                output_text TEXT,
                settings TEXT,
                created_at TEXT NOT NULL)"""
        )


def add_record(input_type: str, original: str, output: str, settings: dict) -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO history (input_type, original_text, output_text, settings, created_at) "
            "VALUES (?,?,?,?,?)",
            (input_type, (original or "")[:MAX_STORED_CHARS], output or "",
             json.dumps(settings or {}), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        return cur.lastrowid


def get_history(limit: int = 200) -> pd.DataFrame:
    with _conn() as con:
        rows = con.execute(
            "SELECT id, input_type, created_at, settings, output_text FROM history "
            "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return pd.DataFrame([dict(r) for r in rows],
                        columns=["id", "input_type", "created_at", "settings", "output_text"])


def get_record(record_id: int):
    with _conn() as con:
        row = con.execute("SELECT * FROM history WHERE id=?", (record_id,)).fetchone()
    return dict(row) if row else None


def delete_record(record_id: int) -> None:
    with _conn() as con:
        con.execute("DELETE FROM history WHERE id=?", (record_id,))


def clear_history() -> None:
    with _conn() as con:
        con.execute("DELETE FROM history")