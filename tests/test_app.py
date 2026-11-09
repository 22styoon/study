import sqlite3
from fastapi.testclient import TestClient
from app import db
from app.main import app

def test_dashboard_and_session(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "학습 시작" in response.text
        assert client.get("/favicon.ico").status_code == 204
        response = client.post("/sessions/start", data={"study_date": "2026-11-09"})
        assert response.status_code == 303
    conn = sqlite3.connect(tmp_path / "study.db")
    assert conn.execute("select count(*) from sessions").fetchone()[0] == 1

def test_upload_rejects_unsupported(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    with TestClient(app, follow_redirects=False) as client:
        client.get("/")
        response = client.post("/submissions", data={"assignment_id": "A-20261109-01"}, files={"file": ("x.txt", b"bad", "text/plain")})
        assert response.status_code == 303
