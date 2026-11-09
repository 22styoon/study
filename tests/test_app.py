import sqlite3
from fastapi.testclient import TestClient
from app import db
from app.main import app

def test_dashboard_and_session(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "학습 시작" in response.text
        assert "katex.min.css" in response.text
        assert "pointerType!=='pen'" in response.text
        assert client.get("/favicon.ico").status_code == 204
        response = client.post("/sessions/start", data={"study_date": "2026-11-09"})
        assert response.status_code == 303
    conn = sqlite3.connect(tmp_path / "study.db")
    assert conn.execute("select count(*) from sessions").fetchone()[0] == 1

def test_previous_day_session_does_not_disable_today_start(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    with db.connection() as conn:
        conn.execute("INSERT INTO sessions(study_date,scheduled_start_at,attendance_status) VALUES(?,?,?)", ("2026-11-08", "2026-11-08T19:00:00+09:00", "CHECKED_IN"))
    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "disabled" not in response.text

def test_upload_rejects_unsupported(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    with TestClient(app, follow_redirects=False) as client:
        client.get("/dashboard")
        response = client.post("/submissions", data={"assignment_id": "A-20261109-01"}, files={"file": ("x.txt", b"bad", "text/plain")})
        assert response.status_code == 303

def test_separate_topic_problem_and_proof_pages(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/topic/A-20261109-T02").status_code == 200
        assert client.get("/problem/A-20261109-T02").status_code == 200
        assert client.get("/proof/A-20261109-T02").status_code == 200
