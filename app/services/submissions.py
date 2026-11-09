from __future__ import annotations
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from app.db import DATA_DIR, connection, event

ALLOWED = {".jpg", ".jpeg", ".png", ".pdf"}

def receive_file(assignment_id: str, source: Path) -> dict:
    if source.suffix.lower() not in ALLOWED or not source.is_file():
        raise ValueError("허용 형식은 JPG, JPEG, PNG, PDF이며 파일이 존재해야 합니다.")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    dest_dir = DATA_DIR / "submissions"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{assignment_id}-{digest[:12]}{source.suffix.lower()}"
    shutil.copy2(source, dest)
    received = datetime.now().astimezone().isoformat(timespec="seconds")
    with connection() as conn:
        duplicate = conn.execute("SELECT id FROM submissions WHERE assignment_id=? AND sha256=?", (assignment_id, digest)).fetchone()
        if duplicate:
            return {"id": duplicate[0], "duplicate": True, "sha256": digest}
        row = conn.execute("SELECT deadline_at FROM assignments WHERE id=?", (assignment_id,)).fetchone()
        if row is None:
            raise ValueError("존재하지 않는 과제입니다.")
        revision = conn.execute("SELECT COALESCE(MAX(revision_number),0)+1 FROM submissions WHERE assignment_id=?", (assignment_id,)).fetchone()[0]
        deadline_status = "ON_TIME" if received <= row[0] else "LATE"
        cur = conn.execute("INSERT INTO submissions(assignment_id,file_path,sha256,received_at,deadline_status,file_status,revision_number) VALUES(?,?,?,?,?,?,?)", (assignment_id, str(dest), digest, received, deadline_status, "VALID", revision))
        result = {"id": cur.lastrowid, "duplicate": False, "sha256": digest, "deadline_status": deadline_status, "revision_number": revision}
    event("SUBMISSION_RECEIVED", assignment_id, result)
    return result
