import base64
from app import db
from app.services.proofs import submit_proof

def test_text_proof_is_queued_for_review(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    result = submit_proof("A-20261109-T02", "Let x be in...", None)
    assert result["verification_status"] == "PENDING_REVIEW"
    with db.connection() as conn:
        row = conn.execute("select proof_text, image_path from proofs where id=?", (result["id"],)).fetchone()
    assert row[0] == "Let x be in..."
    assert row[1] is None

def test_handwriting_png_is_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    monkeypatch.setattr(db, "DATA_DIR", tmp_path / "data")
    db.init_db()
    png_data = "data:image/png;base64," + base64.b64encode(b"png bytes").decode()
    result = submit_proof("L-20261109-T02", "", png_data)
    with db.connection() as conn:
        image_path = conn.execute("select image_path from proofs where id=?", (result["id"],)).fetchone()[0]
    assert image_path.endswith(".png")

def test_empty_proof_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    try:
        submit_proof("A-20261109-T01", "", None)
    except ValueError as exc:
        assert "하나 이상" in str(exc)
    else:
        raise AssertionError("empty proof was accepted")
