import sqlite3
from .config import DB_PATH, SIGNS_DIR

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create tables and register every .mp4 in assets/signs as a sign.
    File name = gloss, e.g. thank_you.mp4 -> THANK_YOU."""
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS signs(
            gloss TEXT PRIMARY KEY,
            video_path TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS aliases(
            alias TEXT PRIMARY KEY,
            gloss TEXT NOT NULL REFERENCES signs(gloss)
        );
        """)
        for f in SIGNS_DIR.glob("*.mp4"):
            con.execute("INSERT OR REPLACE INTO signs VALUES(?,?)",
                        (f.stem.upper(), str(f)))
        # optional aliases (extend as you grow the vocabulary)
        for alias, gloss in [("HI", "HELLO"), ("THANKS", "THANK_YOU")]:
            if con.execute("SELECT 1 FROM signs WHERE gloss=?", (gloss,)).fetchone():
                con.execute("INSERT OR REPLACE INTO aliases VALUES(?,?)", (alias, gloss))

def vocabulary() -> list[str]:
    with connect() as con:
        return [r[0] for r in con.execute("SELECT gloss FROM signs ORDER BY gloss")]

def find(gloss: str):
    g = gloss.strip().upper().replace(" ", "_")
    with connect() as con:
        row = con.execute(
            "SELECT gloss, video_path FROM signs WHERE gloss=? "
            "UNION SELECT s.gloss, s.video_path FROM aliases a "
            "JOIN signs s ON s.gloss=a.gloss WHERE a.alias=?", (g, g)).fetchone()
    return row