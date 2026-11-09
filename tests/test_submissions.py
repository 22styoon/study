from pathlib import Path
from app import db
from app.services.submissions import receive_file

def test_duplicate_submission_is_not_a_new_revision(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    source = tmp_path / "answer.jpg"
    source.write_bytes(b"image bytes")
    first = receive_file("A-20261109-01", source)
    second = receive_file("A-20261109-01", source)
    assert first["duplicate"] is False
    assert second["duplicate"] is True
    with db.connection() as conn:
        assert conn.execute("select count(*) from submissions").fetchone()[0] == 1

def test_unsupported_extension_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    source = tmp_path / "answer.exe"
    source.write_bytes(b"not allowed")
    try:
        receive_file("A-20261109-01", source)
    except ValueError as exc:
        assert "허용 형식" in str(exc)
    else:
        raise AssertionError("unsupported file was accepted")
