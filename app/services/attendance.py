from datetime import datetime
from app.db import connection, event

def start_session(study_date: str) -> dict:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with connection() as conn:
        cur = conn.execute("INSERT INTO sessions(study_date,scheduled_start_at,check_in_at,attendance_status) VALUES(?,?,?,?)", (study_date, now, now, "CHECKED_IN"))
        session_id = cur.lastrowid
    event("SESSION_STARTED", str(session_id), {"study_date": study_date, "check_in_at": now})
    return {"id": session_id, "check_in_at": now, "attendance_status": "CHECKED_IN"}
