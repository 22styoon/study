from __future__ import annotations
import base64
import binascii
from pathlib import Path
from datetime import datetime
from app.db import DATA_DIR, connection, event

MAX_IMAGE_BYTES = 10 * 1024 * 1024

def submit_proof(topic_id: str, proof_text: str | None, proof_image_data: str | None) -> dict:
    text = (proof_text or "").strip()
    if not text and not proof_image_data:
        raise ValueError("증명 텍스트 또는 손글씨를 하나 이상 제출해야 합니다.")
    image_path = None
    if proof_image_data:
        if "," in proof_image_data:
            header, encoded = proof_image_data.split(",", 1)
            if header != "data:image/png;base64":
                raise ValueError("손글씨 이미지는 PNG 캔버스 데이터만 허용됩니다.")
        else:
            encoded = proof_image_data
        try:
            image = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("손글씨 이미지 데이터를 읽을 수 없습니다.") from exc
        if len(image) > MAX_IMAGE_BYTES:
            raise ValueError("손글씨 이미지가 너무 큽니다.")
        image_dir = DATA_DIR / "proofs"
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / f"{topic_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
        image_path.write_bytes(image)
    submitted_at = datetime.now().astimezone().isoformat(timespec="seconds")
    with connection() as conn:
        if conn.execute("SELECT 1 FROM topics WHERE id=?", (topic_id,)).fetchone() is None:
            raise ValueError("존재하지 않는 명제/정리입니다.")
        cur = conn.execute("INSERT INTO proofs(topic_id,proof_text,image_path,submitted_at,verification_status) VALUES(?,?,?,?,?)", (topic_id, text or None, str(image_path) if image_path else None, submitted_at, "PENDING_REVIEW"))
        proof_id = cur.lastrowid
    result = {"id": proof_id, "topic_id": topic_id, "verification_status": "PENDING_REVIEW", "submitted_at": submitted_at}
    event("PROOF_SUBMITTED", str(proof_id), result)
    return result
