import base64
from app import db
from app.services.proofs import submit_proof

def test_multi_page_proof_is_queued_for_review(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    page = "data:image/png;base64," + base64.b64encode(b"page bytes").decode()
    result = submit_proof("A-20261109-T02", proof_pages_data="[" + repr(page).replace("'", '"') + "]")
    assert result["verification_status"] == "PENDING_REVIEW"
    with db.connection() as conn:
        row = conn.execute("select proof_text, image_path from proofs where id=?", (result["id"],)).fetchone()
        page_count = conn.execute("select count(*) from proof_pages where proof_id=?", (result["id"],)).fetchone()[0]
    assert row[0] is None
    assert row[1].endswith(".png")
    assert page_count == 1

def test_handwriting_png_is_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    monkeypatch.setattr(db, "DATA_DIR", tmp_path / "data")
    db.init_db()
    png_data = "data:image/png;base64," + base64.b64encode(b"png bytes").decode()
    result = submit_proof("L-20261109-T02", proof_pages_data="[" + repr(png_data).replace("'", '"') + "]")
    with db.connection() as conn:
        image_path = conn.execute("select image_path from proofs where id=?", (result["id"],)).fetchone()[0]
    assert image_path.endswith(".png")

def test_empty_proof_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "study.db")
    db.init_db()
    try:
        submit_proof("A-20261109-T01", proof_pages_data="[]")
    except ValueError as exc:
        assert "1~20" in str(exc)
    else:
        raise AssertionError("empty proof was accepted")
