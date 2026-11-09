from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "study.db"

def utc_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

@contextmanager
def connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    with connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS assignments (id TEXT PRIMARY KEY, study_date TEXT NOT NULL, subject TEXT NOT NULL, title TEXT NOT NULL, deadline_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'OPEN', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, study_date TEXT NOT NULL, scheduled_start_at TEXT NOT NULL, check_in_at TEXT, check_out_at TEXT, declared_focus_minutes INTEGER DEFAULT 0, attendance_status TEXT NOT NULL DEFAULT 'NOT_STARTED');
        CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, assignment_id TEXT NOT NULL, file_path TEXT NOT NULL, sha256 TEXT NOT NULL, received_at TEXT NOT NULL, deadline_status TEXT NOT NULL, file_status TEXT NOT NULL, revision_number INTEGER NOT NULL DEFAULT 1, UNIQUE(assignment_id, sha256));
        CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, target_id TEXT, event_at TEXT NOT NULL, payload_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS topics (id TEXT PRIMARY KEY, assignment_id TEXT NOT NULL, subject TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL, statement TEXT NOT NULL, source_reference TEXT, prerequisites TEXT NOT NULL DEFAULT '[]', learning_state TEXT NOT NULL DEFAULT 'NOT_STARTED');
        CREATE TABLE IF NOT EXISTS proofs (id INTEGER PRIMARY KEY AUTOINCREMENT, topic_id TEXT NOT NULL, proof_text TEXT, image_path TEXT, submitted_at TEXT NOT NULL, verification_status TEXT NOT NULL DEFAULT 'PENDING_REVIEW', feedback TEXT, FOREIGN KEY(topic_id) REFERENCES topics(id));
        """)
        if conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0] == 0:
            rows = [("A-20261109-01", "2026-11-09", "Real Analysis", "Sets and Functions", "2026-11-09T21:40:00+09:00"), ("L-20261109-01", "2026-11-09", "Linear Algebra", "Vector Spaces", "2026-11-10T00:30:00+09:00")]
            conn.executemany("INSERT INTO assignments VALUES (?,?,?,?,?,'OPEN',?)", [(*row, utc_now()) for row in rows])
        if conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 0:
            topics = [
                ("A-20261109-T01", "A-20261109-01", "Real Analysis", "definition", "Set", "A set is a well-defined collection of objects.", "Stoll §1.1", '["basic logic"]', "NOT_STARTED"),
                ("A-20261109-T02", "A-20261109-01", "Real Analysis", "theorem", "De Morgan's Laws", "For sets A and B, (A ∪ B)^c = A^c ∩ B^c and (A ∩ B)^c = A^c ∪ B^c.", "Stoll §1.1", '["Set"]', "NOT_STARTED"),
                ("L-20261109-T01", "L-20261109-01", "Linear Algebra", "definition", "Vector Space", "A vector space over a field F is a set V with addition and scalar multiplication satisfying the vector space axioms.", "Friedberg §1.2", '["basic algebra"]', "NOT_STARTED"),
                ("L-20261109-T02", "L-20261109-01", "Linear Algebra", "theorem", "Subspace Criterion", "A nonempty subset W of V is a subspace if it is closed under addition and scalar multiplication.", "Friedberg §1.3", '["Vector Space"]', "NOT_STARTED"),
            ]
            conn.executemany("INSERT INTO topics VALUES (?,?,?,?,?,?,?,?,?)", topics)
        conn.execute("UPDATE topics SET statement=? WHERE id=?", (r"For sets $A$ and $B$, $(A \\cup B)^c = A^c \\cap B^c$ and $(A \\cap B)^c = A^c \\cup B^c$.", "A-20261109-T02"))
        conn.execute("UPDATE topics SET statement=? WHERE id=?", (r"A nonempty subset $W$ of $V$ is a subspace if it is closed under addition and scalar multiplication.", "L-20261109-T02"))

def event(event_type: str, target_id: str | None, payload: dict) -> None:
    with connection() as conn:
        conn.execute("INSERT INTO events(event_type,target_id,event_at,payload_json) VALUES (?,?,?,?)", (event_type, target_id, utc_now(), json.dumps(payload, ensure_ascii=False)))
