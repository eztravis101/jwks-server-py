import sqlite3
import os

DB_FILE = "totally_not_my_privateKeys.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            kid TEXT PRIMARY KEY,
            n TEXT NOT NULL,
            e TEXT NOT NULL,
            d TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def store_key(kid: str, n: str, e: str, d: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO keys (kid, n, e, d) VALUES (?, ?, ?, ?)",
        (kid, n, e, d)
    )
    conn.commit()
    conn.close()

def load_keys_from_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT kid, n, e, d FROM keys")
    rows = cur.fetchall()
    conn.close()
    return [{"kid": r[0], "n": r[1], "e": r[2], "d": r[3]} for r in rows]

def get_valid_keys():
    return load_keys_from_db()
