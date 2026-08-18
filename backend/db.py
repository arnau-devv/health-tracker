import sqlite3
import os

DB_PATH = "app.db"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "db_schema.sql")

def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite no aplica FKs por defecto
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()